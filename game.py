"""
game.py
Gestion de la création d'équipe et de la boucle de combat.
"""
import random
from models import Personnage, Monstre, Equipe
from utils import (
    get_tous_personnages,
    get_monstre_aleatoire,
    sauvegarder_score,
    afficher_liste_personnages,
    afficher_equipe,
    saisir_entier,
    SEPARATEUR,
)

TAILLE_EQUIPE = 3
