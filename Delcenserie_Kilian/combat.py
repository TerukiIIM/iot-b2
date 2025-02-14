import random
import time
from rfid import scan_rfid, rfid1, rfid2
from database import get_pokemon_by_uid
from display import display_text, clear_line
from machine import Pin

btn_up = Pin(14, Pin.IN, Pin.PULL_UP)
btn_down = Pin(15, Pin.IN, Pin.PULL_UP)
btn_select = Pin(16, Pin.IN, Pin.PULL_UP)

def display_message(message, line=0):

    display_text(message, line)  # Affiche à la ligne spécifiée

def display_battle_info(player_pokemon, enemy_pokemon, show_vs=False):
    if show_vs:
        display_message(player_pokemon.name, line=0)
        display_message("VS", line=1)
        display_message(enemy_pokemon.name, line=2)

def select_attack(pokemon):
    index = 0
    while True:
        # Effacer l'écran avant d'afficher de nouvelles attaques
        display_message(f"{pokemon.name}", line=0)
        
        # Calculer les indices d'attaque à afficher en fonction de la position
        attack_index_1 = (index) % 4
        attack_index_2 = (index + 1) % 4

        # Affichage des attaques sur deux lignes
        display_message(f"> {pokemon.moves[attack_index_1][0]}", line=1)  # Première ligne (attaque sélectionnée)
        display_message(f"  {pokemon.moves[attack_index_2][0]}", line=2)  # Deuxième ligne (autre attaque)

        # Défilement des attaques avec les boutons
        if not btn_up.value():  # Défilement vers le haut
            index = (index - 1) % 4
            time.sleep(0.2)
        elif not btn_down.value():  # Défilement vers le bas
            index = (index + 1) % 4
            time.sleep(0.2)
        elif not btn_select.value():  # Validation
            return pokemon.moves[index]

def compute_damage(attack, attacker, defender):
    power = attack[2]
    type_advantage = 2 if attack[1] == defender.weakness else 1
    damage = max(1, (attacker.attack * power) // defender.defense * type_advantage)
    return damage

def battle(player_pokemon, enemy_pokemon):
    display_battle_info(player_pokemon, enemy_pokemon, show_vs=True)  # Affiche "VS" une seule fois au début
    time.sleep(1)  # Petite pause après l'affichage des Pokémon

    while player_pokemon.is_alive() and enemy_pokemon.is_alive():
        # Tour du joueur : Choisir une attaque
        attack = select_attack(player_pokemon)
        damage = compute_damage(attack, player_pokemon, enemy_pokemon)
        enemy_pokemon.take_damage(damage)
        
        # Afficher le résultat de l'attaque
        display_message(f" {attack[0]}", line=0)
        display_message(f"{enemy_pokemon.name} - {damage} HP!", line=1)
        display_message(f"PV: {enemy_pokemon.hp}/{enemy_pokemon.max_hp}", line=2)
        time.sleep(1)

        if not enemy_pokemon.is_alive():
            display_message(f"{enemy_pokemon.name} est K.O. !", line=0)
            time.sleep(2)
            break

        # Tour de l'adversaire : Choisir une attaque
        attack_probs = [0.4, 0.3, 0.2, 0.1]  # Probabilités pour chaque attaque
        cumulative_probs = []
        total = 0

        for prob in attack_probs:
            total += prob
            cumulative_probs.append(total)

        rand_val = random.random() * total

        for i, cumulative_prob in enumerate(cumulative_probs):
            if rand_val < cumulative_prob:
                enemy_attack = enemy_pokemon.moves[i]
                break

        # Afficher l'attaque de l'adversaire
        damage = compute_damage(enemy_attack, enemy_pokemon, player_pokemon)
        player_pokemon.take_damage(damage)
        display_message(f" {enemy_attack[0]}", line=0)
        display_message(f"{player_pokemon.name} - {damage} HP!", line=1)
        display_message(f"PV: {player_pokemon.hp}/{player_pokemon.max_hp}", line=2)
        time.sleep(1)

        if not player_pokemon.is_alive():
            display_message(f"{player_pokemon.name} est K.O. !", line=0)
            break

        # Retour à la sélection des attaques pour le joueur
        time.sleep(1)

    return True

def ask_restart():
    """Affiche un message pour demander si l'utilisateur veut relancer le combat avec choix Oui/Non."""
    options = ["Relancer Combat?", "Oui", "Non"]
    selected = 1  # Par défaut, l'utilisateur choisit "Oui"

    while True:
        display_message(f"{options[0]}", line=0)
        display_message(f"  > {options[1]}" if selected == 1 else f"    {options[1]}", line=1)
        display_message(f"  > {options[2]}" if selected == 2 else f"    {options[2]}", line=2)
        
        if not btn_up.value():  # Défilement vers le haut
            selected = 1 if selected == 2 else selected - 1
            time.sleep(0.2)
        elif not btn_down.value():  # Défilement vers le bas
            selected = 2 if selected == 1 else selected + 1
            time.sleep(0.2)
        elif not btn_select.value():  # Sélection
            if selected == 1:
                return True  # Relancer le combat
            else:
                display_message("Merci d'avoir joué !", line=0)
                time.sleep(2)
                return False

def combat():
    display_message("Mode Combat", line=0)
    time.sleep(1)

    # Sélection des Pokémon
    display_message("Scanne ton Pokémon", line=0)
    player_uid = None
    while not player_uid:
        player_uid = scan_rfid(rfid1)
    
    display_message("Scanne l'adversaire", line=0)
    opponent_uid = None
    while not opponent_uid:
        opponent_uid = scan_rfid(rfid2)

    player = get_pokemon_by_uid(player_uid)
    opponent = get_pokemon_by_uid(opponent_uid)
    
    if not player or not opponent:
        display_message("Erreur: Pokémon inconnu", line=0)
        return
    
    # Affichage des Pokémon après la sélection
    display_battle_info(player, opponent, show_vs=True)
    time.sleep(1)

    # Réinitialisation des PV des Pokémon avant de commencer le combat
    player.hp = player.max_hp
    opponent.hp = opponent.max_hp

    # Combat en boucle
    if battle(player, opponent):
        if ask_restart():
            combat()  # Relance le combat
        else:
            return  # Fin du jeu
