import time
from machine import Pin
from display import display_text
from combat import combat  # Import du module combat

btn_start = Pin(16, Pin.IN, Pin.PULL_UP)  # Bouton pour démarrer le jeu
btn_up = Pin(14, Pin.IN, Pin.PULL_UP)
btn_down = Pin(15, Pin.IN, Pin.PULL_UP)

# État du jeu
combat_in_progress = False  # Booléen pour savoir si un combat est en cours
modes = ["Démarrer le Combat"]
selected = 0

def menu():
    """Affiche le menu principal et attend la sélection de l'utilisateur."""
    global combat_in_progress  # Accès à la variable globale

    while True:
        display_text(f"> {modes[selected]}")  # Affichage de l'option

        # Si le bouton "Start" est pressé et qu'un combat n'est pas en cours
        if not btn_start.value() and not combat_in_progress:
            print("Bouton pressé, lancement du combat")  # Message de débogage
            combat_in_progress = True  # Le combat commence, donc combat_in_progress devient True

            # Appel du combat
            combat_result = combat()  # Le combat renvoie True/False selon la fin du combat

            combat_in_progress = False  # Combat terminé, revenir au menu
            print("Combat terminé.")  # Message de débogage

            # Attendre un court délai avant de revenir au menu pour éviter que le bouton ne soit pris en compte immédiatement
            time.sleep(1)  # Un délai un peu plus long pour éviter un rebond

            # Après le combat, on relance le menu pour démarrer un autre combat
            display_text("Voulez-vous relancer un combat ?")
            time.sleep(1)  # Attente pour afficher le message

            # L'option pour relancer un combat
            while True:
                display_text("Relancer Combat? Oui ou Non")  # Affiche un prompt pour la relance

                # Si l'utilisateur appuie sur le bouton de démarrage pour relancer un combat
                if not btn_start.value():
                    break  # Relancer le combat

                # Si un bouton est pressé pour sortir du menu, on sort de cette boucle et on retourne au menu
                time.sleep(0.1)

            continue  # Retour à la boucle pour relancer un combat si l'utilisateur veut

        # Si un combat est terminé, la boucle recommence et tu peux relancer un nouveau combat
        time.sleep(0.1)  # Petit délai pour éviter de trop charger le processeur

menu()
