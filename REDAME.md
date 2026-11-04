# ⚔️ Jeu de Combat par Vagues

Jeu en ligne de commande en Python. Les personnages, les monstres et les scores sont stockés dans MongoDB.
Le joueur compose une équipe de 3 personnages et affronte des monstres aléatoires, vague après vague, jusqu'à la défaite.

## Prérequis

- Python >= 3.8
- MongoDB démarré (par défaut sur `localhost:27017`)
- pymongo :

```bash
pip install -r requirements.txt
```

## Structure du projet

```
jeu_video_python/
├── main.py            # Menu principal et point d'entrée
├── db_init.py         # Initialisation de la base MongoDB
├── game.py            # Création d'équipe et logique de combat
├── models.py          # Classes Combattant, Personnage, Monstre, Equipe
├── utils.py           # Connexion DB, classement, affichage, saisies sécurisées
├── base_de_donnees/
│   ├── personnages.json     # 10 personnages jouables (import Compass / mongoimport)
│   ├── monstres.json        # 10 monstres
├── tests/
│   └── test_models.py # Tests unitaires (sans MongoDB)
├── requirements.txt
└── README.md
```

## Base de données

Le jeu lit et écrit **en direct** dans MongoDB : le serveur doit être démarré à chaque partie
(MongoDB Compass n'est qu'une interface graphique, il est optionnel).

Base : `jeu_video`

| Collection    | Champs                          | Contenu                                  |
|---------------|---------------------------------|------------------------------------------|
| `personnages` | `nom, attaque, defense, pv`     | 10 personnages jouables                  |
| `monstres`    | `nom, attaque, defense, pv`     | 10 monstres                              |
| `scores`      | `joueur, vagues, date`          | historique des parties (top 3 affiché)   |

Index : `nom` unique sur `personnages` et `monstres` ; `(vagues ↓, date ↑)` sur `scores`
(à égalité de vagues, le score le plus ancien passe devant).

Le dossier `base_de_donnees/` permet de recréer la base **sans Python**, de trois façons :

**A. Script `init_db.js` (le plus simple)**

```bash
mongosh base_de_donnees/init_db.js
```

Ou, dans MongoDB Compass : **Open MongoDB shell**, puis coller le contenu du fichier.
Deux réglages en haut du script : `RESET_SCORES` (efface le classement) et
`SCORES_EXEMPLE` (ajoute 3 scores de démonstration).

**B. Import des fichiers JSON dans Compass**

Créer la base `jeu_video`, puis pour chaque collection :
**Add Data → Import JSON or CSV file** (`personnages.json`, `monstres.json`,
et `scores_exemple.json` si besoin).

**C. Ligne de commande `mongoimport`**

```bash
mongoimport --db jeu_video --collection personnages --jsonArray --file base_de_donnees/personnages.json
mongoimport --db jeu_video --collection monstres    --jsonArray --file base_de_donnees/monstres.json
mongoimport --db jeu_video --collection scores      --jsonArray --file base_de_donnees/scores_exemple.json
```

> Ces trois méthodes donnent le même résultat que `python db_init.py`.

## Lancement

### 1. Initialiser la base de données

Au choix : le script Python ci-dessous, ou les fichiers de `base_de_donnees/` (voir plus haut).

```bash
python db_init.py                 # insère personnages et monstres, garde les scores
python db_init.py --reset-scores  # efface aussi le classement
```

> Si la base est vide au lancement, `main.py` l'initialise automatiquement.

### 2. Lancer le jeu

```bash
python main.py
```

### Configuration (optionnel)

| Variable      | Défaut                       |
|---------------|------------------------------|
| `MONGO_URI`   | `mongodb://localhost:27017/` |
| `MONGO_DB`    | `jeu_video`                  |

### Tests

```bash
python -m unittest discover tests
```

## Déroulement d'une partie

1. **Menu principal** : Démarrer le jeu / Afficher le classement / Quitter.
2. **Nom d'utilisateur** : non vide, 20 caractères maximum.
3. **Création de l'équipe** : affichage de l'équipe actuelle puis de la liste des personnages
   (`Nom - X ATK - X DEF - X PV`). Chaque personnage ne peut être choisi qu'une seule fois.
   Tape `0` pour retirer le dernier personnage ajouté. L'équipe est validée à la fin (o/n).
4. **Combat** : un monstre aléatoire est tiré de la base et ses caractéristiques sont affichées.
   - Chaque personnage vivant attaque le monstre **en premier**.
   - Le monstre attaque ensuite un personnage vivant au hasard.
   - Dégâts = ATK de l'attaquant − DEF de la cible (minimum 0).
   - Monstre à 0 PV → victoire, le compteur de vagues augmente de 1 et une nouvelle vague commence.
   - Tous les personnages à 0 PV → défaite, fin de partie.
5. **Fin de partie** : le score (nombre de vagues survécues) est enregistré, avec le rang du joueur
   et le **top 3** des meilleurs scores.

`Ctrl+C` pendant les combats abandonne la partie, et le score est quand même enregistré.

## Personnages

| Nom        | ATK | DEF | PV  |
|------------|-----|-----|-----|
| Guerrier   | 15  | 10  | 100 |
| Mage       | 20  |  5  |  80 |
| Archer     | 18  |  7  |  90 |
| Voleur     | 22  |  8  |  85 |
| Paladin    | 14  | 12  | 110 |
| Sorcier    | 25  |  3  |  70 |
| Chevalier  | 17  | 15  | 120 |
| Moine      | 19  |  9  |  95 |
| Berserker  | 23  |  6  | 105 |
| Chasseur   | 16  | 11  | 100 |

## Monstres

| Nom        | ATK | DEF | PV  |
|------------|-----|-----|-----|
| Gobelin    | 10  |  5  |  50 |
| Orc        | 20  |  8  | 120 |
| Dragon     | 35  | 20  | 300 |
| Zombie     | 12  |  6  |  70 |
| Troll      | 25  | 15  | 200 |
| Spectre    | 18  | 10  | 100 |
| Golem      | 30  | 25  | 250 |
| Vampire    | 22  | 12  | 150 |
| Loup-garou | 28  | 18  | 180 |
| Squelette  | 15  |  7  |  90 |