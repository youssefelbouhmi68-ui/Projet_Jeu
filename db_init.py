"""
db_init.py
Initialise la base MongoDB avec les personnages et les monstres.

    python db_init.py                 # (ré)insère personnages et monstres, garde les scores
    python db_init.py --reset-scores  # efface aussi le classement
"""

# argparse : lit les options tapées dans le terminal (ex : --reset-scores)
import argparse
# sys : sert à renvoyer un code de sortie au système (0 = tout va bien)
import sys

# Constantes de tri pour les index MongoDB (croissant / décroissant)
from pymongo import ASCENDING, DESCENDING
# Type d'erreur levée par pymongo quand MongoDB pose problème
from pymongo.errors import PyMongoError

# Fonctions de connexion et erreur personnalisée, écrites dans utils.py
from utils import get_db, verifier_connexion, fermer_connexion, ErreurBaseDeDonnees

# Liste des 10 personnages : un dictionnaire par personnage
PERSONNAGES = [
    {"nom": "Guerrier",   "attaque": 15, "defense": 10, "pv": 100},
    {"nom": "Mage",       "attaque": 20, "defense":  5, "pv":  80},
    {"nom": "Archer",     "attaque": 18, "defense":  7, "pv":  90},
    {"nom": "Voleur",     "attaque": 22, "defense":  8, "pv":  85},
    {"nom": "Paladin",    "attaque": 14, "defense": 12, "pv": 110},
    {"nom": "Sorcier",    "attaque": 25, "defense":  3, "pv":  70},
    {"nom": "Chevalier",  "attaque": 17, "defense": 15, "pv": 120},
    {"nom": "Moine",      "attaque": 19, "defense":  9, "pv":  95},
    {"nom": "Berserker",  "attaque": 23, "defense":  6, "pv": 105},
    {"nom": "Chasseur",   "attaque": 16, "defense": 11, "pv": 100},
]

# Liste des 10 monstres : même format que les personnages
MONSTRES = [
    {"nom": "Gobelin",    "attaque": 10, "defense":  5, "pv":  50},
    {"nom": "Orc",        "attaque": 20, "defense":  8, "pv": 120},
    {"nom": "Dragon",     "attaque": 35, "defense": 20, "pv": 300},
    {"nom": "Zombie",     "attaque": 12, "defense":  6, "pv":  70},
    {"nom": "Troll",      "attaque": 25, "defense": 15, "pv": 200},
    {"nom": "Spectre",    "attaque": 18, "defense": 10, "pv": 100},
    {"nom": "Golem",      "attaque": 30, "defense": 25, "pv": 250},
    {"nom": "Vampire",    "attaque": 22, "defense": 12, "pv": 150},
    {"nom": "Loup-garou", "attaque": 28, "defense": 18, "pv": 180},
    {"nom": "Squelette",  "attaque": 15, "defense":  7, "pv":  90},
]


# Remplit la base ; reset_scores=True efface aussi le classement
def init_db(reset_scores=False):
    """(Ré)insère personnages et monstres ; le classement est conservé par défaut."""
    # Récupère la base de données MongoDB "jeu_video"
    db = get_db()

    # Supprime la collection des personnages (évite les doublons si on relance)
    db.personnages.drop()
    # Supprime la collection des monstres
    db.monstres.drop()
    # Copies : insert_many ajoute un champ _id aux dictionnaires passés
    # Insère les 10 personnages (en copies pour ne pas modifier la liste d'origine)
    db.personnages.insert_many([dict(p) for p in PERSONNAGES])
    # Insère les 10 monstres (en copies aussi)
    db.monstres.insert_many([dict(m) for m in MONSTRES])
    # Index unique sur le nom : deux personnages ne peuvent pas avoir le même nom
    db.personnages.create_index([("nom", ASCENDING)], unique=True)
    # Même règle pour les monstres
    db.monstres.create_index([("nom", ASCENDING)], unique=True)

    # Si on a demandé de remettre le classement à zéro
    if reset_scores:
        # On supprime toute la collection des scores
        db.scores.drop()
    # Index pour trier vite le classement : plus de vagues d'abord, puis le plus ancien
    db.scores.create_index([("vagues", DESCENDING), ("date", ASCENDING)])

    # Affiche le nombre de personnages présents en base
    print(f"  ✅  {db.personnages.count_documents({})} personnages insérés.")
    # Affiche le nombre de monstres présents en base
    print(f"  ✅  {db.monstres.count_documents({})} monstres insérés.")
    # Si le classement a été effacé
    if reset_scores:
        # On le dit à l'utilisateur
        print("  ✅  Classement réinitialisé.")
    # Sinon, le classement a été gardé
    else:
        # On affiche combien de scores sont conservés
        print(f"  ✅  Classement conservé ({db.scores.count_documents({})} score(s)).")


# Fonction principale : lit les options, lance l'initialisation, gère les erreurs
def main():
    # Crée le lecteur d'options avec une description du programme
    parser = argparse.ArgumentParser(description="Initialise la base MongoDB du jeu.")
    # Déclare l'option --reset-scores (vraie si elle est tapée, fausse sinon)
    parser.add_argument("--reset-scores", action="store_true",
                        help="efface aussi l'historique des scores")
    # Lit ce que l'utilisateur a tapé dans le terminal
    args = parser.parse_args()

    # On essaie de tout faire en capturant les erreurs possibles
    try:
        # Vérifie que MongoDB répond
        verifier_connexion()
        # Remplit la base (reset_scores vient de l'option tapée)
        init_db(reset_scores=args.reset_scores)
    # Erreur lisible prévue par notre code (MongoDB éteint...)
    except ErreurBaseDeDonnees as e:
        # Affiche le message d'erreur
        print(f"\n  ❌ {e}\n")
        # Code 1 = le programme s'est terminé avec une erreur
        return 1
    # Erreur interne de MongoDB / pymongo
    except PyMongoError as e:
        # Affiche le détail de l'erreur
        print(f"\n  ❌ Erreur MongoDB : {e}\n")
        # Code 1 = erreur
        return 1
    # Dans tous les cas (succès ou erreur), on ferme la connexion proprement
    finally:
        fermer_connexion()

    # Si on arrive ici, tout s'est bien passé : message de fin
    print("\n  🎮 Base de données prête ! Lance le jeu avec : python main.py")
    # Code 0 = succès
    return 0


# Ce bloc ne s'exécute que si on lance directement ce fichier (pas si on l'importe)
if __name__ == "__main__":
    # Lance main() et utilise son résultat (0 ou 1) comme code de sortie
    sys.exit(main())