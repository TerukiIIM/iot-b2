from pokemon import Pokemon

pokemon_db = {
    "35-25-51-2-11": Pokemon(
        "35-25-51-2-11", "Carapuce", 50, 50, 10, 5, "Eau", "Plante",
        [("Pistolet à O", "Eau", 10), ("Morsure", "Normal", 8), ("Hydrocanon", "Eau", 20), ("Coquilame", "Eau", 15)]
    ),
    "90-75-51-2-32": Pokemon(
        "90-75-51-2-32", "Salamèche", 45, 45, 12, 4, "Feu", "Eau",
        [("Flammèche", "Feu", 10), ("Griffe", "Normal", 7), ("Lance-Flammes", "Feu", 18), ("Rafale Feu", "Feu", 20)]
    ),
    "211-248-49-2-24": Pokemon(
        "211-248-49-2-24", "Bulbizarre", 55, 55, 9, 6, "Plante", "Feu",
        [("Fouet Lianes", "Plante", 9), ("Charge", "Normal", 6), ("Tranch'Herbe", "Plante", 14), ("Lance-Soleil", "Plante", 22)]
    ),
    "83-228-150-226-195": Pokemon(
        "83-228-150-226-195", "Moustillon", 50, 50, 10, 5, "Eau", "Plante",
        [("Bulles d'O", "Eau", 10), ("Coquilame", "Eau", 15), ("Hydroqueue", "Eau", 18), ("Aqua-Jet", "Eau", 12)]
    ),
    "19-86-231-228-70": Pokemon(
        "19-86-231-228-70", "Gruikui", 45, 45, 12, 4, "Feu", "Eau",
        [("Charge", "Normal", 7), ("Flamboiement", "Feu", 12), ("Nitrocharge", "Feu", 14), ("Boutefeu", "Feu", 20)]
    ),
    "19-62-238-228-39": Pokemon(
        "19-62-238-228-39", "Vipélierre", 55, 55, 9, 6, "Plante", "Feu",
        [("Vampigraine", "Plante", 8), ("Tranch'Herbe", "Plante", 14), ("Tempête Verte", "Plante", 18), ("Giga-Sangsue", "Plante", 20)]
    ),
}

def get_pokemon_by_uid(uid):
    return pokemon_db.get(uid, None)
