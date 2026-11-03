"""
game.py
Création de l'équipe et boucle de combat par vagues.
"""

import random

from models import Personnage, Monstre, Equipe
from utils import (
    get_tous_personnages,
    get_monstre_aleatoire,
    sauvegarder_score,
    get_rang,
    afficher_liste_personnages,
    afficher_equipe,
    barre_pv,
    saisir_entier,
    demander_confirmation,
    pause,
    ErreurBaseDeDonnees,
    SEPARATEUR,
    LIGNE,
)

TAILLE_EQUIPE = 3


# ── Création d'équipe ────────────────────────────────────────────────────────

def creer_equipe():
    