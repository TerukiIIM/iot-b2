import machine
import ssd1306
import time

# Configuration des pins pour les boutons
btn_up = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)  # Bouton pour monter
btn_down = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)  # Bouton pour descendre
btn_select = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)  # Bouton pour afficher l'attaque sélectionnée

# Configuration I2C pour l'écran OLED
i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0), freq=100000)
oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Liste des attaques
attacks = ["Bulles d'O", "Hydrocanon", "Coquilame", "Aire d'eau"]
selected = 0  # Index de l'attaque sélectionnée
display_attack = ""  # Variable pour stocker l'attaque sélectionnée à afficher en bas

# Fonction pour afficher le menu
def display_menu():
    oled.fill(0)  # Efface l'écran
    for i in range(2):  # Affiche seulement deux attaques à la fois
        if selected + i < len(attacks):  # Vérifie qu'on n'a pas dépassé la liste
            if i == 0:  # Première ligne (attaque actuelle)
                oled.text("-> " + attacks[selected + i], 0, i * 10 + 10)  # Attaque sélectionnée
            else:  # Deuxième ligne (attaque suivante)
                oled.text("   " + attacks[selected + i], 0, i * 10 + 10)
    
    # Afficher l'attaque sélectionnée en bas (si elle est définie)
    if display_attack:
        oled.text( display_attack, 0, 0)  # Affiche l'attaque sélectionnée dans les derniers pixels

    oled.show()

# Fonction de gestion des boutons
def check_buttons():
    global selected, display_attack
    if not btn_up.value():  # Si le bouton haut est appuyé
        selected = (selected - 1) % len(attacks)  # Descendre dans la liste (boucle)
        time.sleep(0.2)  # Anti-rebond
    elif not btn_down.value():  # Si le bouton bas est appuyé
        selected = (selected + 1) % len(attacks)  # Monter dans la liste (boucle)
        time.sleep(0.2)  # Anti-rebond
    elif not btn_select.value():  # Si le troisième bouton est appuyé
        display_attack = attacks[selected]  # Enregistrer l'attaque sélectionnée
        time.sleep(0.2)  # Anti-rebond

# Boucle principale
while True:
    display_menu()  # Affiche le menu avec les attaques
    check_buttons()  # Vérifie si un bouton a été appuyé

