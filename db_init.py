"""
db_init.py
Initialise la base MongoDB avec les personnages et les monstres.

    python db_init.py                 # (ré)insère personnages et monstres, garde les scores
    python db_init.py --reset-scores  # efface aussi le classement
"""

import argparse
import sys

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

from utils import get_db, verifier_connexion, fermer_connexion, ErreurBaseDeDonnees

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


def init_db(reset_scores=False):
    """(Ré)insère personnages et monstres ; le classement est conservé par défaut."""
    db = get_db()

    db.personnages.drop()
    db.monstres.drop()
    # Copies : insert_many ajoute un champ _id aux dictionnaires passés
    db.personnages.insert_many([dict(p) for p in PERSONNAGES])
    db.monstres.insert_many([dict(m) for m in MONSTRES])
    db.personnages.create_index([("nom", ASCENDING)], unique=True)
    db.monstres.create_index([("nom", ASCENDING)], unique=True)

    if reset_scores:
        db.scores.drop()
    db.scores.create_index([("vagues", DESCENDING), ("date", ASCENDING)])

    print(f"  ✅  {db.personnages.count_documents({})} personnages insérés.")
    print(f"  ✅  {db.monstres.count_documents({})} monstres insérés.")
    if reset_scores:
        print("  ✅  Classement réinitialisé.")
    else:
        print(f"  ✅  Classement conservé ({db.scores.count_documents({})} score(s)).")


def main():
    parser = argparse.ArgumentParser(description="Initialise la base MongoDB du jeu.")
    parser.add_argument("--reset-scores", action="store_true",
                        help="efface aussi l'historique des scores")
    args = parser.parse_args()

    try:
        verifier_connexion()
        init_db(reset_scores=args.reset_scores)
    except ErreurBaseDeDonnees as e:
        print(f"\n  ❌ {e}\n")
        return 1
    except PyMongoError as e:
        print(f"\n  ❌ Erreur MongoDB : {e}\n")
        return 1
    finally:
        fermer_connexion()

    print("\n  🎮 Base de données prête ! Lance le jeu avec : python main.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
