"""
models.py
Classes du jeu : Combattant (classe de base), Personnage, Monstre, Equipe.
"""


class Combattant:
    """Classe de base commune aux personnages et aux monstres."""

    def __init__(self, nom, attaque, defense, pv):
        attaque, defense, pv = int(attaque), int(defense), int(pv)
        if attaque < 0 or defense < 0 or pv <= 0:
            raise ValueError(f"Caractéristiques invalides pour {nom} : "
                             f"ATK={attaque}, DEF={defense}, PV={pv}")
        self.nom = str(nom)
        self.attaque = attaque
        self.defense = defense
        self.pv_max = pv
        self.pv = pv

    def est_vivant(self):
        return self.pv > 0

    def degats_contre(self, cible):
        """Dégâts que ce combattant infligerait à la cible (sans l'attaquer)."""
        return max(0, self.attaque - cible.defense)

    def recevoir_degats(self, degats_bruts):
        """La défense réduit les dégâts reçus de sa valeur (minimum 0)."""
        degats = max(0, degats_bruts - self.defense)
        self.pv = max(0, self.pv - degats)
        return degats

    def attaquer(self, cible):
        return cible.recevoir_degats(self.attaque)

    def __str__(self):
        return (f"{self.nom} - {self.attaque} ATK - {self.defense} DEF - "
                f"{self.pv}/{self.pv_max} PV")

    def __repr__(self):
        return (f"{type(self).__name__}(nom={self.nom!r}, attaque={self.attaque}, "
                f"defense={self.defense}, pv={self.pv}/{self.pv_max})")

    @classmethod
    def depuis_dict(cls, data):
        """Construit l'objet à partir d'un document MongoDB."""
        try:
            return cls(nom=data["nom"], attaque=data["attaque"],
                       defense=data["defense"], pv=data["pv"])
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Document invalide pour {cls.__name__} : {data!r}") from e


class Personnage(Combattant):
    """Personnage jouable."""


class Monstre(Combattant):
    """Monstre affronté pendant les vagues."""


class Equipe:
    """Équipe de personnages (chaque personnage ne peut y figurer qu'une fois)."""

    def __init__(self, taille_max=3):
        self.taille_max = taille_max
        self.personnages = []

    def __len__(self):
        return len(self.personnages)

    def est_complete(self):
        return len(self.personnages) >= self.taille_max

    def contient(self, nom):
        return any(p.nom == nom for p in self.personnages)

    def ajouter(self, personnage):
        if self.est_complete():
            raise ValueError("L'équipe est déjà complète.")
        if self.contient(personnage.nom):
            raise ValueError(f"{personnage.nom} est déjà dans l'équipe.")
        self.personnages.append(personnage)

    def retirer_dernier(self):
        return self.personnages.pop() if self.personnages else None

    def est_en_vie(self):
        return any(p.est_vivant() for p in self.personnages)

    def membres_vivants(self):
        return [p for p in self.personnages if p.est_vivant()]

    def __str__(self):
        if not self.personnages:
            return "     (vide)"
        lignes = []
        for i, p in enumerate(self.personnages, 1):
            statut = "" if p.est_vivant() else "  💀 [K.O.]"
            lignes.append(f"  {i}. {p}{statut}")
        return "\n".join(lignes)