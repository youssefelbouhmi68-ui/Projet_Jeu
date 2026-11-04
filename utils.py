"""
utils.py
Fonctions utilitaires : connexion DB, accès aux données, classement,
affichage et saisies utilisateur sécurisées.
"""

# os : permet de lire les variables d'environnement
import os
# datetime : pour enregistrer la date des scores (timezone = fuseau horaire)
from datetime import datetime, timezone

# MongoClient : se connecter à MongoDB ; ASCENDING / DESCENDING : sens des tris
from pymongo import MongoClient, ASCENDING, DESCENDING
# Type d'erreur de pymongo, pour l'attraper
from pymongo.errors import PyMongoError

# ── Configuration (surchargeable par variables d'environnement) ──────────────

# Adresse du serveur MongoDB (valeur par défaut si la variable MONGO_URI n'existe pas)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
# Nom de la base de données (valeur par défaut : jeu_video)
DB_NAME = os.environ.get("MONGO_DB", "jeu_video")
# Nombre de scores affichés dans le classement
TAILLE_CLASSEMENT = 3
# Longueur maximale du nom du joueur
LONGUEUR_NOM_MAX = 20

# Grande ligne double pour les titres
SEPARATEUR = "═" * 56
# Ligne simple pour séparer les blocs
LIGNE = "─" * 56


# Erreur personnalisée : permet d'afficher un message clair au lieu d'une trace technique
class ErreurBaseDeDonnees(Exception):
    """Erreur lisible liée à MongoDB (connexion, données manquantes...)."""


# ── Connexion (un seul client partagé) ───────────────────────────────────────

# Le client MongoDB, vide au départ (créé à la première utilisation)
_client = None


# Retourne la base de données
def get_db():
    """Retourne la base MongoDB (le client est créé une seule fois)."""
    # On indique qu'on modifie la variable globale _client
    global _client
    # Si le client n'existe pas encore
    if _client is None:
        # On le crée ; si MongoDB ne répond pas, on abandonne après 3 secondes
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    # On retourne la base choisie dans ce client
    return _client[DB_NAME]


# Teste que MongoDB répond
def verifier_connexion():
    """Vérifie que MongoDB répond, sinon lève une erreur explicite."""
    # On essaie d'envoyer un "ping" au serveur
    try:
        get_db().client.admin.command("ping")
    # Si ça échoue (serveur éteint, mauvaise adresse...)
    except PyMongoError as e:
        # On lève notre erreur lisible, avec l'erreur d'origine en cause
        raise ErreurBaseDeDonnees(
            f"Impossible de se connecter à MongoDB ({MONGO_URI}).\n"
            "     → Vérifie que le serveur MongoDB est bien démarré."
        ) from e


# Ferme la connexion à MongoDB
def fermer_connexion():
    # On indique qu'on modifie la variable globale _client
    global _client
    # Si une connexion existe
    if _client is not None:
        # On la ferme
        _client.close()
        # On remet la variable à vide
        _client = None


# Dit si la base contient déjà des données
def base_est_initialisee():
    # Récupère la base
    db = get_db()
    # Vrai s'il y a au moins un personnage ET au moins un monstre
    return (db.personnages.count_documents({}) > 0
            and db.monstres.count_documents({}) > 0)


# ── Récupération des données ─────────────────────────────────────────────────

# Retourne tous les personnages
def get_tous_personnages():
    """Retourne tous les personnages (ordre d'insertion)."""
    # find({}, {"_id": 0}) : tous les documents sans le champ _id, triés par _id croissant
    return list(get_db().personnages.find({}, {"_id": 0}).sort("_id", ASCENDING))


# Retourne un monstre pris au hasard
def get_monstre_aleatoire():
    """Retourne un document monstre tiré aléatoirement."""
    # $sample demande à MongoDB un document au hasard
    resultats = list(get_db().monstres.aggregate([{"$sample": {"size": 1}}]))
    # Si la collection est vide
    if not resultats:
        # Message clair pour l'utilisateur
        raise ErreurBaseDeDonnees("Aucun monstre en base. Lance d'abord : python db_init.py")
    # On prend le seul document obtenu
    doc = resultats[0]
    # On retire le champ technique _id (inutile pour le jeu)
    doc.pop("_id", None)
    # On renvoie le monstre
    return doc


# ── Scores / classement ──────────────────────────────────────────────────────

# Enregistre le score d'une partie
def sauvegarder_score(nom_joueur, vagues):
    """Enregistre le score (tout l'historique est conservé)."""
    # Ajoute un document : joueur, nombre de vagues, date UTC du moment
    get_db().scores.insert_one({
        "joueur": nom_joueur,
        "vagues": int(vagues),
        "date": datetime.now(timezone.utc),
    })


# Retourne les meilleurs scores
def get_classement(limite=TAILLE_CLASSEMENT):
    """Meilleurs scores ; à égalité, le plus ancien passe devant."""
    # On enchaîne : recherche, tri, puis limitation du nombre de résultats
    return list(
        get_db().scores.find({}, {"_id": 0})
        .sort([("vagues", DESCENDING), ("date", ASCENDING)])
        .limit(limite)
    )


# Calcule le rang d'un score
def get_rang(vagues):
    """Rang d'un score parmi tous les scores enregistrés (1 = meilleur)."""
    # Collection des scores
    scores = get_db().scores
    # Rang = nombre de scores strictement meilleurs + 1 ; et on renvoie aussi le total
    return scores.count_documents({"vagues": {"$gt": vagues}}) + 1, scores.count_documents({})


# ── Affichage ────────────────────────────────────────────────────────────────

# Affiche le titre du jeu
def afficher_titre():
    # Ligne vide puis séparateur
    print("\n" + SEPARATEUR)
    # Titre centré à la main
    print("             ⚔️   JEU DE COMBAT PAR VAGUES   ⚔️")
    # Séparateur du bas
    print(SEPARATEUR)


# Affiche le top des meilleurs scores
def afficher_classement():
    # Récupère les meilleurs scores en base
    classement = get_classement()
    # Ligne vide puis séparateur
    print("\n" + SEPARATEUR)
    # Titre du classement
    print(f"               🏆  TOP {TAILLE_CLASSEMENT} DES MEILLEURS SCORES  🏆")
    # Séparateur du bas du titre
    print(SEPARATEUR)
    # S'il n'y a aucun score
    if not classement:
        # On le dit
        print("  Aucun score enregistré pour le moment.")
    # Sinon on affiche chaque score
    else:
        # Médailles pour les 3 premiers
        medailles = ["🥇", "🥈", "🥉"]
        # On parcourt les scores avec leur position (i commence à 0)
        for i, entree in enumerate(classement):
            # Médaille si disponible, sinon le numéro de place
            medaille = medailles[i] if i < len(medailles) else f"{i + 1}."
            # On récupère la date du score (peut être absente)
            date = entree.get("date")
            # On la met au format jj/mm/aaaa, ou vide si elle n'existe pas
            date_txt = date.strftime("%d/%m/%Y") if isinstance(date, datetime) else ""
            # Ligne : médaille, nom aligné à gauche, vagues, date
            print(f"  {medaille}  {entree.get('joueur', '?'):<{LONGUEUR_NOM_MAX}} "
                  f"{entree.get('vagues', 0):>4} vague(s)   {date_txt}")
    # Séparateur de fin
    print(SEPARATEUR)


# Affiche la liste des personnages à choisir
def afficher_liste_personnages(personnages, equipe):
    # Ligne vide puis ligne simple
    print("\n" + LIGNE)
    # Titre de la liste
    print("  PERSONNAGES DISPONIBLES")
    # Ligne sous le titre
    print(LIGNE)
    # On parcourt les personnages en les numérotant à partir de 1
    for i, p in enumerate(personnages, 1):
        # Si le personnage est déjà dans l'équipe, on ajoute une mention
        deja = "  ✔ déjà choisi" if equipe.contient(p["nom"]) else ""
        # Ligne : numéro, nom, attaque, défense, PV, mention éventuelle
        print(f"  {i:>2}. {p['nom']:<12} {p['attaque']:>3} ATK - {p['defense']:>3} DEF"
              f" - {p['pv']:>4} PV{deja}")
    # Ligne de fin
    print(LIGNE)


# Affiche l'équipe en cours de création
def afficher_equipe(equipe, titre="📋 Équipe actuelle"):
    # Titre avec le nombre de personnages : (2/3)
    print(f"\n  {titre} ({len(equipe)}/{equipe.taille_max}) :")
    # Liste des personnages (utilise la méthode __str__ de Equipe)
    print(str(equipe))


# Construit une barre de vie en texte
def barre_pv(combattant, largeur=20):
    """Barre de vie textuelle, ex : ██████████░░░░░░░░░░"""
    # Nombre de carrés pleins proportionnel aux PV restants
    plein = round(largeur * combattant.pv / combattant.pv_max) if combattant.pv_max else 0
    # S'il reste des PV, on affiche au moins un carré plein
    if combattant.pv > 0:
        plein = max(1, plein)
    # Carrés pleins puis carrés vides pour compléter la largeur
    return "█" * plein + "░" * (largeur - plein)


# ── Saisies utilisateur sécurisées ───────────────────────────────────────────

# Version sécurisée de input()
def lire(message=""):
    """input() qui transforme une fin de saisie (Ctrl+D / EOF) en interruption propre."""
    # On essaie de lire ce que tape l'utilisateur
    try:
        return input(message)
    # Si l'entrée est fermée (Ctrl+D)
    except EOFError:
        # Retour à la ligne pour garder l'affichage propre
        print()
        # On la transforme en interruption, gérée proprement par le reste du jeu
        raise KeyboardInterrupt from None


# Met le jeu en pause jusqu'à Entrée
def pause(message="  [Appuie sur Entrée pour continuer...]"):
    # Affiche le message et attend que le joueur appuie sur Entrée
    lire(message)


# Demande un nombre entier dans un intervalle
def saisir_entier(message, min_val, max_val):
    """Demande un entier compris entre min_val et max_val (bornes incluses)."""
    # On répète jusqu'à obtenir une valeur correcte
    while True:
        # On lit la saisie et on retire les espaces autour
        saisie = lire(message).strip()
        # On essaie de convertir en entier
        try:
            valeur = int(saisie)
        # Si ce n'est pas un nombre entier
        except ValueError:
            # On prévient l'utilisateur
            print("  ⚠️  Entrée invalide. Entre un nombre entier.")
            # On recommence la boucle
            continue
        # Si le nombre est dans l'intervalle autorisé
        if min_val <= valeur <= max_val:
            # On le renvoie : fin de la fonction
            return valeur
        # Sinon on indique l'intervalle attendu (et la boucle recommence)
        print(f"  ⚠️  Entre un nombre entre {min_val} et {max_val}.")


# Demande le nom du joueur
def saisir_nom():
    """Demande un nom d'utilisateur non vide et de longueur raisonnable."""
    # On répète jusqu'à obtenir un nom valide
    while True:
        # split() + join() : supprime les espaces en trop (début, fin, doublons)
        nom = " ".join(lire("  Ton nom d'utilisateur : ").split())  # espaces nettoyés
        # Si le nom est vide
        if not nom:
            # On refuse
            print("  ⚠️  Le nom ne peut pas être vide.")
        # S'il est trop long
        elif len(nom) > LONGUEUR_NOM_MAX:
            # On refuse en indiquant la limite
            print(f"  ⚠️  {LONGUEUR_NOM_MAX} caractères maximum.")
        # S'il contient des caractères invisibles ou de contrôle
        elif not nom.isprintable():
            # On refuse
            print("  ⚠️  Le nom contient des caractères invalides.")
        # Sinon le nom est valide
        else:
            # On le renvoie
            return nom


# Pose une question oui/non
def demander_confirmation(message):
    """Question oui/non. Retourne True pour oui."""
    # On répète jusqu'à obtenir une réponse comprise
    while True:
        # On lit la réponse, sans espaces, en minuscules
        reponse = lire(message).strip().lower()
        # Réponses qui veulent dire oui
        if reponse in ("o", "oui", "y", "yes"):
            return True
        # Réponses qui veulent dire non
        if reponse in ("n", "non", "no"):
            return False
        # Réponse non reconnue : on explique (et la boucle recommence)
        print("  ⚠️  Réponds par 'o' (oui) ou 'n' (non).")