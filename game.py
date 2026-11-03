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
    """Le joueur compose son équipe de 3 personnages (sans doublon)."""
    tous = get_tous_personnages()
    if len(tous) < TAILLE_EQUIPE:
        raise ErreurBaseDeDonnees("Pas assez de personnages en base. Lance : python db_init.py")

    while True:
        equipe = Equipe(TAILLE_EQUIPE)

        while not equipe.est_complete():
            afficher_equipe(equipe)
            afficher_liste_personnages(tous, equipe)
            print(f"  Slot {len(equipe) + 1}/{TAILLE_EQUIPE} — choisis un personnage "
                  f"(1-{len(tous)}), ou 0 pour retirer le dernier ajouté.")
            choix = saisir_entier("  > ", 0, len(tous))

            if choix == 0:
                retire = equipe.retirer_dernier()
                print(f"  ↩️  {retire.nom} retiré de l'équipe." if retire
                      else "  ⚠️  L'équipe est vide, rien à retirer.")
                continue

            data = tous[choix - 1]
            if equipe.contient(data["nom"]):
                print(f"  ⚠️  {data['nom']} est déjà dans ton équipe. Choisis-en un autre.")
                continue

            perso = Personnage.depuis_dict(data)
            equipe.ajouter(perso)
            print(f"  ✅  {perso.nom} ajouté à l'équipe !")

        print("\n" + SEPARATEUR)
        afficher_equipe(equipe, titre="⚔️  Équipe finale")
        print(SEPARATEUR)
        if demander_confirmation("  Valider cette équipe ? (o/n) : "):
            return equipe
        print("  🔄 On recommence la composition de l'équipe.")


# ── Combat ───────────────────────────────────────────────────────────────────

def _afficher_etat_combat(equipe, monstre, vague):
    print(f"\n{LIGNE}")
    print(f"  🌊 VAGUE {vague}")
    print(LIGNE)
    print(f"  👹 Monstre : {monstre}")
    print(f"     {barre_pv(monstre)}")
    print(LIGNE)
    print("  🗡️  Ton équipe :")
    for p in equipe.personnages:
        etat = barre_pv(p) if p.est_vivant() else "💀 K.O."
        print(f"     {p.nom:<12} {p.pv:>4}/{p.pv_max:<4} PV  {etat}")
    print(LIGNE)


def combat_bloque(equipe, monstre):
    """
    Vrai si plus personne ne peut blesser personne (ATK <= DEF des deux côtés) :
    sans ce garde-fou, le combat tournerait à l'infini.
    """
    vivants = equipe.membres_vivants()
    return (all(p.degats_contre(monstre) == 0 for p in vivants)
            and all(monstre.degats_contre(p) == 0 for p in vivants))


def combattre_vague(equipe, monstre, vague, attendre=True):
    """
    Résout un combat entre l'équipe et le monstre.
    Les personnages attaquent avant le monstre.
    Retourne True si l'équipe gagne, False si elle est vaincue.
    """
    _afficher_etat_combat(equipe, monstre, vague)
    if attendre:
        pause("\n  [Appuie sur Entrée pour commencer le combat...]")

    tour = 0
    while monstre.est_vivant() and equipe.est_en_vie():
        if combat_bloque(equipe, monstre):
            print(f"\n  🛡️  Personne ne peut blesser l'autre : {monstre.nom} abandonne et s'enfuit !")
            return True

        tour += 1
        print(f"\n  ── Tour {tour} ──")

        # Phase 1 : chaque personnage vivant attaque le monstre
        for perso in equipe.membres_vivants():
            degats = perso.attaquer(monstre)
            print(f"  ⚔️  {perso.nom} inflige {degats} dégâts → {monstre.nom} : {monstre.pv} PV")
            if not monstre.est_vivant():
                break

        if not monstre.est_vivant():
            break

        # Phase 2 : le monstre attaque un personnage vivant au hasard
        cible = random.choice(equipe.membres_vivants())
        degats = monstre.attaquer(cible)
        print(f"  💥 {monstre.nom} attaque {cible.nom} → {degats} dégâts "
              f"({cible.nom} : {cible.pv} PV)")
        if not cible.est_vivant():
            print(f"  💀 {cible.nom} est hors combat !")

    if not monstre.est_vivant():
        print(f"\n  🎉 Victoire ! {monstre.nom} est vaincu en {tour} tour(s) !")
        return True

    print("\n  💀 Défaite... Toute l'équipe a été vaincue.")
    return False


# ── Partie complète ──────────────────────────────────────────────────────────

def lancer_partie(nom_joueur):
    """Lance une partie : création d'équipe puis vagues infinies jusqu'à la défaite."""
    print(f"\n  Bienvenue, {nom_joueur} ! Compose ton équipe.")
    equipe = creer_equipe()

    vagues_survecues = 0
    abandon = False
    print("\n  🚀 Le combat commence ! (Ctrl+C pour abandonner — ton score sera gardé)")

    try:
        while True:
            vague = vagues_survecues + 1
            monstre = Monstre.depuis_dict(get_monstre_aleatoire())

            if not combattre_vague(equipe, monstre, vague):
                break  # défaite

            vagues_survecues += 1
            print(f"\n  🌟 Tu as survécu à la vague {vague} ! "
                  f"Vagues survécues : {vagues_survecues}")
            pause("  [Appuie sur Entrée pour la prochaine vague...]")
    except KeyboardInterrupt:
        abandon = True
        print("\n\n  🏳️  Partie abandonnée.")

    # ── Fin de partie ────────────────────────────────────────────────────────
    sauvegarder_score(nom_joueur, vagues_survecues)
    rang, total = get_rang(vagues_survecues)
    rang_txt = "1er" if rang == 1 else f"{rang}e"

    print(f"\n{SEPARATEUR}")
    print(f"  🏁 Partie terminée{' (abandon)' if abandon else ''}, {nom_joueur} !")
    print(f"     Ton score : {vagues_survecues} vague(s) survécue(s)")
    print(f"     Classement : {rang_txt} sur {total} partie(s) jouée(s)")
    if rang == 1 and vagues_survecues > 0:
        print("     🏆 NOUVEAU RECORD !")
    print("  ✅  Score sauvegardé.")
    print(SEPARATEUR)

    return vagues_survecues