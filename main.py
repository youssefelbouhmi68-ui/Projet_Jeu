"""
main.py
Point d'entrée du jeu — menu principal.

    python main.py
"""

# sys : pour renvoyer un code de sortie au système
import sys

# Type d'erreur de pymongo, pour l'attraper
from pymongo.errors import PyMongoError

# On importe db_init pour pouvoir remplir la base automatiquement si elle est vide
import db_init
# La fonction qui gère une partie complète
from game import lancer_partie
# Fonctions et constantes utiles, écrites dans utils.py
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


# Prépare la base avant de jouer
def preparer_base():
    """Vérifie la connexion et initialise la base automatiquement si elle est vide."""
    # Vérifie que MongoDB répond (sinon erreur claire)
    verifier_connexion()
    # Si la base est vide
    if not base_est_initialisee():
        # On prévient le joueur
        print("\n  ℹ️  Base vide détectée → initialisation automatique...")
        # On remplit la base avec personnages et monstres
        db_init.init_db()


# Affiche le menu et renvoie le choix du joueur
def menu_principal():
    # Titre du jeu
    afficher_titre()
    # Option 1
    print("  1. Démarrer le jeu")
    # Option 2
    print("  2. Afficher le classement")
    # Option 3
    print("  3. Quitter")
    # Ligne de séparation
    print(SEPARATEUR)
    # Demande un nombre entre 1 et 3 et le renvoie
    return saisir_entier("  Ton choix : ", 1, 3)


# Boucle du menu : revient au menu jusqu'à ce que le joueur quitte
def boucle_menu():
    # Répète indéfiniment
    while True:
        # Affiche le menu et récupère le choix
        choix = menu_principal()

        # Choix 1 : jouer
        if choix == 1:
            # On protège la partie contre Ctrl+C / Ctrl+D
            try:
                # Demande le nom du joueur
                nom = saisir_nom()
                # Lance la partie complète
                lancer_partie(nom)
            # Si le joueur interrompt pendant la saisie du nom ou la création d'équipe
            except KeyboardInterrupt:
                # On l'informe qu'on retourne au menu
                print("\n  ↩️  Retour au menu principal.")
                # On repart au début de la boucle (menu)
                continue
            # Après la partie, on affiche le classement
            afficher_classement()
            # On attend Entrée avant de réafficher le menu
            pause()

        # Choix 2 : classement
        elif choix == 2:
            # Affiche les meilleurs scores
            afficher_classement()
            # Attend Entrée
            pause()

        # Choix 3 : quitter
        else:
            # return sort de la boucle (et donc du menu)
            return


# Fonction principale du programme
def main():
    # Code de retour : 0 = tout va bien
    code_retour = 0
    # On protège tout le programme contre les erreurs prévues
    try:
        # Vérifie MongoDB et remplit la base si besoin
        preparer_base()
        # Lance le menu principal
        boucle_menu()
    # Ctrl+C ou Ctrl+D dans un menu
    except KeyboardInterrupt:
        # Retour à la ligne pour garder l'affichage propre, puis on quitte
        print()
    # Erreur lisible prévue (MongoDB éteint, base vide...)
    except ErreurBaseDeDonnees as e:
        # Affiche le message d'erreur
        print(f"\n  ❌ {e}\n")
        # Code 1 = erreur
        code_retour = 1
    # Erreur interne de MongoDB
    except PyMongoError as e:
        # Affiche le détail
        print(f"\n  ❌ Erreur MongoDB : {e}\n")
        # Code 1 = erreur
        code_retour = 1
    # Dans tous les cas, on ferme la connexion à la fin
    finally:
        fermer_connexion()

    # Message d'au revoir seulement si tout s'est bien passé
    if code_retour == 0:
        print("\n  À bientôt ! 👋\n")
    # Renvoie le code de sortie
    return code_retour


# Ce bloc ne s'exécute que si on lance directement ce fichier
if __name__ == "__main__":
    # Lance main() et utilise son résultat comme code de sortie
    sys.exit(main())