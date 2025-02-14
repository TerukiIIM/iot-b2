class Pokemon:
    def __init__(self, uid, name, hp, max_hp, attack, defense, element, weakness, moves):
        self.uid = uid  # Identifiant unique
        self.name = name  # Nom du Pokémon
        self.hp = hp  # Points de vie actuels
        self.max_hp = max_hp  # Points de vie maximum
        self.attack = attack  # Statistique d'attaque
        self.defense = defense  # Statistique de défense
        self.element = element  # Élément du Pokémon (ex: Eau, Feu, Plante)
        self.weakness = weakness  # Faiblesse du Pokémon (ex: Eau contre Feu)
        self.moves = moves  # Liste des attaques possibles du Pokémon

    def is_alive(self):
        """Retourne True si le Pokémon est vivant (HP > 0), sinon False."""
        return self.hp > 0

    def take_damage(self, damage):
        """Réduit les points de vie du Pokémon en fonction des dégâts reçus."""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0  # Assure que les PV ne tombent pas en dessous de 0
