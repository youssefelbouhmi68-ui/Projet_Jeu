"""
main.py
Point d'entrée du jeu — menu principal.
    python main.py
"""

from utils import afficher_titre, afficher_classement, saisir_entier, saisir_nom, SEPARATEUR
from game import lancer_partie


def menu_principal():
    afficher_titre()
    print("  1. Démarrer le jeu")
    print("  2. Afficher le classement")
    print("  3. Quitter")
    print(SEPARATEUR)
    return saisir_entier("  Ton choix : ", 1, 3)


def main():
    while True:
        choix = menu_principal()

        if choix == 1:
            nom = saisir_nom()
            vagues = lancer_partie(nom)
            afficher_classement()

        elif choix == 2:
            afficher_classement()

        elif choix == 3:
            print("\n  À bientôt ! 👋\n")
            break


if __name__ == "__main__":
    main()