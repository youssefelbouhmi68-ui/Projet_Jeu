"""
models.py
Classes du jeu : Combattant (classe de base), Personnage, Monstre, Equipe.
"""


# Classe de base : contient tout ce qui est commun aux personnages et aux monstres
class Combattant:
    """Classe de base commune aux personnages et aux monstres."""

    # Constructeur : appelé quand on crée un combattant (ex : Combattant("Mage", 20, 5, 80))
    def __init__(self, nom, attaque, defense, pv):
        # On convertit les trois valeurs en entiers (au cas où elles arrivent en texte)
        attaque, defense, pv = int(attaque), int(defense), int(pv)
        # On refuse les valeurs absurdes : stats négatives ou PV à 0 ou moins
        if attaque < 0 or defense < 0 or pv <= 0:
            # On arrête avec une erreur claire qui indique les valeurs fautives
            raise ValueError(f"Caractéristiques invalides pour {nom} : "
                             f"ATK={attaque}, DEF={defense}, PV={pv}")
        # On mémorise le nom (converti en texte)
        self.nom = str(nom)
        # On mémorise la puissance d'attaque
        self.attaque = attaque
        # On mémorise la défense
        self.defense = defense
        # On mémorise les PV maximum (pour les barres de vie)
        self.pv_max = pv
        # Les PV actuels commencent au maximum
        self.pv = pv

    # Dit si le combattant est encore en vie
    def est_vivant(self):
        # Vrai tant qu'il lui reste au moins 1 PV
        return self.pv > 0

    # Calcule les dégâts qu'on infligerait à une cible, sans l'attaquer vraiment
    def degats_contre(self, cible):
        """Dégâts que ce combattant infligerait à la cible (sans l'attaquer)."""
        # Attaque moins défense de la cible, jamais en dessous de 0
        return max(0, self.attaque - cible.defense)

    # Fait subir une attaque au combattant
    def recevoir_degats(self, degats_bruts):
        """La défense réduit les dégâts reçus de sa valeur (minimum 0)."""
        # On retire la défense aux dégâts bruts, sans descendre sous 0
        degats = max(0, degats_bruts - self.defense)
        # On enlève les dégâts aux PV, sans descendre sous 0
        self.pv = max(0, self.pv - degats)
        # On renvoie les dégâts réellement subis (pour l'affichage)
        return degats

    # Attaque une cible
    def attaquer(self, cible):
        # La cible reçoit l'attaque de ce combattant et renvoie les dégâts subis
        return cible.recevoir_degats(self.attaque)

    # Texte affiché quand on fait print(combattant)
    def __str__(self):
        # Format : Nom - X ATK - X DEF - PV actuels/PV max PV
        return (f"{self.nom} - {self.attaque} ATK - {self.defense} DEF - "
                f"{self.pv}/{self.pv_max} PV")

    # Texte technique (utile pour déboguer, affiché dans la console Python)
    def __repr__(self):
        # Affiche le type de la classe (Personnage ou Monstre) et toutes les valeurs
        return (f"{type(self).__name__}(nom={self.nom!r}, attaque={self.attaque}, "
                f"defense={self.defense}, pv={self.pv}/{self.pv_max})")

    # Méthode de classe : sert à fabriquer un objet à partir d'un document MongoDB
    @classmethod
    def depuis_dict(cls, data):
        """Construit l'objet à partir d'un document MongoDB."""
        # On essaie de créer l'objet avec les champs du dictionnaire
        try:
            # cls = la classe appelante (Personnage ou Monstre)
            return cls(nom=data["nom"], attaque=data["attaque"],
                       defense=data["defense"], pv=data["pv"])
        # Si un champ manque, si data n'est pas un dictionnaire, ou si une valeur est invalide
        except (KeyError, TypeError, ValueError) as e:
            # On renvoie une erreur lisible qui montre le document problématique
            raise ValueError(f"Document invalide pour {cls.__name__} : {data!r}") from e


# Un personnage jouable : hérite de tout Combattant
class Personnage(Combattant):
    """Personnage jouable."""


# Un monstre : hérite de tout Combattant
class Monstre(Combattant):
    """Monstre affronté pendant les vagues."""


# L'équipe du joueur : une liste de personnages
class Equipe:
    """Équipe de personnages (chaque personnage ne peut y figurer qu'une fois)."""

    # Constructeur : taille_max vaut 3 par défaut
    def __init__(self, taille_max=3):
        # On mémorise la taille maximale de l'équipe
        self.taille_max = taille_max
        # La liste des personnages commence vide
        self.personnages = []

    # Permet d'écrire len(equipe)
    def __len__(self):
        # Le nombre de personnages dans l'équipe
        return len(self.personnages)

    # Dit si l'équipe est pleine
    def est_complete(self):
        # Vrai quand on a atteint (ou dépassé) la taille maximale
        return len(self.personnages) >= self.taille_max

    # Dit si un personnage de ce nom est déjà dans l'équipe
    def contient(self, nom):
        # Vrai si au moins un personnage porte ce nom
        return any(p.nom == nom for p in self.personnages)

    # Ajoute un personnage à l'équipe
    def ajouter(self, personnage):
        # Si l'équipe est pleine, on refuse
        if self.est_complete():
            raise ValueError("L'équipe est déjà complète.")
        # Si le personnage est déjà dans l'équipe, on refuse (pas de doublon)
        if self.contient(personnage.nom):
            raise ValueError(f"{personnage.nom} est déjà dans l'équipe.")
        # Sinon on l'ajoute à la fin de la liste
        self.personnages.append(personnage)

    # Retire le dernier personnage ajouté
    def retirer_dernier(self):
        # pop() enlève et renvoie le dernier ; si l'équipe est vide on renvoie None
        return self.personnages.pop() if self.personnages else None

    # Dit si l'équipe a encore au moins un survivant
    def est_en_vie(self):
        # Vrai si au moins un personnage est vivant
        return any(p.est_vivant() for p in self.personnages)

    # Liste des personnages encore debout
    def membres_vivants(self):
        # On garde uniquement ceux qui sont vivants
        return [p for p in self.personnages if p.est_vivant()]

    # Texte affiché quand on fait print(equipe)
    def __str__(self):
        # Si l'équipe est vide, on affiche "(vide)"
        if not self.personnages:
            return "     (vide)"
        # Liste qui contiendra une ligne par personnage
        lignes = []
        # On parcourt les personnages en les numérotant à partir de 1
        for i, p in enumerate(self.personnages, 1):
            # Si le personnage est mort, on ajoute l'étiquette K.O.
            statut = "" if p.est_vivant() else "  💀 [K.O.]"
            # On construit la ligne : numéro, description, statut
            lignes.append(f"  {i}. {p}{statut}")
        # On colle toutes les lignes avec un retour à la ligne entre chacune
        return "\n".join(lignes)