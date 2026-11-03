"""
main.py
Point d'entrée du jeu — menu principal.

    python main.py
"""

import sys

from pymongo.errors import PyMongoError

import db_init
from game import lancer_partie
from utils import (
    afficher_titre,
    afficher_classement,
    saisir_entier,
    saisir_nom,
    pause,
    verifier_connexion,
    base_est_initialisee,
    fermer_connexion,
    ErreurBaseDeDonnees,
    SEPARATEUR,
)


def preparer_base():
    """Vérifie la connexion et initialise la base automatiquement si elle est vide."""
    verifier_connexion()
    if not base_est_initialisee():
        print("\n  ℹ️  Base vide détectée → initialisation automatique...")
        db_init.init_db()


def menu_principal():
    afficher_titre()
    print("  1. Démarrer le jeu")
    print("  2. Afficher le classement")
    print("  3. Quitter")
    print(SEPARATEUR)
    return saisir_entier("  Ton choix : ", 1, 3)


def boucle_menu():
    while True:
        choix = menu_principal()

        if choix == 1:
            try:
                nom = saisir_nom()
                lancer_partie(nom)
            except KeyboardInterrupt:
                print("\n  ↩️  Retour au menu principal.")
                continue
            afficher_classement()
            pause()

        elif choix == 2:
            afficher_classement()
            pause()

        else:
            return


def main():
    code_retour = 0
    try:
        preparer_base()
        boucle_menu()
    except KeyboardInterrupt:
        print()  # Ctrl+C / Ctrl+D au menu : on quitte proprement
    except ErreurBaseDeDonnees as e:
        print(f"\n  ❌ {e}\n")
        code_retour = 1
    except PyMongoError as e:
        print(f"\n  ❌ Erreur MongoDB : {e}\n")
        code_retour = 1
    finally:
        fermer_connexion()

    if code_retour == 0:
        print("\n  À bientôt ! 👋\n")
    return code_retour


if __name__ == "__main__":
    sys.exit(main())
