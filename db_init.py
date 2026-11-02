

from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "jeu_video"

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


def init_db():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # Réinitialise les collections pour éviter les doublons
    db.personnages.drop()
    db.monstres.drop()
    db.scores.drop()

    db.personnages.insert_many(PERSONNAGES)
    db.monstres.insert_many(MONSTRES)

    print(f"✅  {db.personnages.count_documents({})} personnages insérés.")
    print(f"✅  {db.monstres.count_documents({})} monstres insérés.")
    print("✅  Collection scores initialisée.")
    print("\n🎮  Base de données prête ! Lance le jeu avec : python main.py")

    client.close()


if __name__ == "__main__":
    init_db()