from machine import Pin, ADC # importe dans le code la lib qui permet de gerer les Pins de sortie
import utime
import neopixel


vrX = ADC(Pin(27))
vrY = ADC(Pin(26))
button = Pin(16, Pin.IN, Pin.PULL_UP)
button2 = Pin(12, Pin.IN, Pin.PULL_UP)
button3 = Pin(9, Pin.IN, Pin.PULL_UP)
pot = ADC(Pin(28))

last_xPos = 0
last_yPos = 0

colors = [(0, 0, 0)] * (16 * 16)
previous_color = (0,0,0)

clear_mode = False  # Mode d'effacement activé/désactivé

def changeDirection(xValue, yValue):
    dirX = 0
    dirY = 0
    res = []
    if xValue < 30000:
        dirX = -1

    elif xValue > 36000:
        dirX = 1

    elif yValue < 30000:
        dirY = -1

    elif yValue > 34000:
        dirY = 1

    res.append((dirX, dirY))
    b2Value = button2.value()
    return dirX, dirY
    







# Initialisation de la matrice
WIDTH = 16  # Largeur de la matrice
HEIGHT = 16  # Hauteur de la matrice
n = WIDTH * HEIGHT  # Nombre total de LEDs
pin = 0  # GPIO connecté au DIN de la matrice
np = neopixel.Neopixel(n,0,pin,"GRB")
np.brightness(1)
#np.set_pixel(0,(250,2,0))
#np.show()

def get_index(x, y):
    """Retourne l'index de la LED dans la matrice 16x16."""
    if x % 2 == 0:
        return x * HEIGHT + y
    else:
        return x * HEIGHT + (HEIGHT - 1 - y)
    
def Calculate(x, y, color):
    """Allume une LED spécifique (x, y) avec une couleur donnée."""
    index = get_index(x, y)
    np.set_pixel(index, color)

    
 

def reset_grid():
    """Réinitialise complètement la grille et oublie toutes les couleurs précédentes."""
    global colors, previous_color
    np.fill((0, 0, 0))  # Éteindre toutes les LEDs
    np.show()
    colors = [(0, 0, 0)] * (16 * 16)  # Réinitialiser les couleurs
    previous_color = (0, 0, 0)  # Réinitialiser la couleur précédente
    
def map_pot_to_color(value):
    """Convertit la valeur du potentiomètre en une couleur RGB avec Jaune et Violet."""
    if value < 13107:  # 0 → 13107 (Rouge → Jaune)
        r = 255
        g = int(value / 13107 * 255)  # Transition vers le jaune
        b = 0
    elif value < 26214:  # 13107 → 26214 (Jaune → Vert)
        r = int((26214 - value) / 13107 * 255)  # Transition vers vert
        g = 255
        b = 0
    elif value < 39321:  # 26214 → 39321 (Vert → Cyan)
        r = 0
        g = 255
        b = int((value - 26214) / 13107 * 255)  # Transition vers cyan
    elif value < 52428:  # 39321 → 52428 (Cyan → Bleu)
        r = 0
        g = int((52428 - value) / 13107 * 255)  # Transition vers bleu
        b = 255
    elif value < 65535:  # 52428 → 65535 (Bleu → Violet)
        r = int((value - 52428) / 13107 * 255)  # Transition vers violet
        g = 0
        b = 255
    else:  # Retour à Rouge
        r, g, b = 255, 0, 0

    return (r, g, b)


# Boucle principale
while True:
    xValue = vrX.read_u16()  # Lire la valeur du joystick X
    yValue = vrY.read_u16()  # Lire la valeur du joystick Y
    potValue = pot.read_u16()
    dirX, dirY = changeDirection(xValue, yValue)
    selected_color = map_pot_to_color(potValue)  # Déterminer la couleur actuelle

    # Calculer la position de la LED à allumer
    xPos = (dirX + last_xPos) % WIDTH  # Utilise une position comprise entre 0 et WIDTH
    yPos = (dirY + last_yPos) % HEIGHT  # Utilise une position comprise entre 0 et HEIGHT
    
    # Vérifier si le bouton "effacer toutes les LEDs sauf la position actuelle" est pressé
    if button.value() == 0:
        reset_grid()
        clear_mode = True 

    # Si le joystick bouge, désactiver le mode effacement
    if dirX != 0 or dirY != 0:
        clear_mode = False  

    # Si on est en mode effacement, ne pas réafficher les anciennes LEDs
    if clear_mode:
        Calculate(xPos, yPos, (0, 255, 0))  # Seule la LED actuelle est allumée
        np.show()
        last_xPos, last_yPos = xPos, yPos
        utime.sleep(0.1)
        continue
    
    Calculate(last_xPos, last_yPos, previous_color)
    
    index = get_index(xPos, yPos)
    
    bValue = button.value()
    if bValue == 0:
        clear_except_current(xPos, yPos)

    # Vérifier si le bouton est pressé
    b2Value = button2.value()
    if b2Value == 0:  # Si le bouton est pressé (value == 0)
        colors[index] = selected_color  # Allumer la LED en rouge
            
    b3Value = button3.value()
    if b3Value == 0:
        if colors[index] != (0,0,0):
            colors[index] = (0, 0, 0)  # Éteindre la LED
            
            
    previous_color = colors[index]
    
    Calculate(xPos, yPos, selected_color)

    # Effacer la matrice avant d'allumer une nouvelle LED
    
    

    # Allumer la LED à la position calculée avec la couleur appropriée
    
    
    for i in range(WIDTH):
        for j in range(HEIGHT):
            if (i, j) != (xPos, yPos):  # Éviter d'écraser la LED verte
                Calculate(i, j, colors[get_index(i, j)])
    
    last_xPos = xPos
    last_yPos = yPos

    # Affichage des valeurs pour le débogage
    print("x value:", xValue, "y value:", yValue, "xPos:", xPos, "yPos:", yPos, "Button:", b2Value, "Potentiomètre", potValue)
    
    np.show()

    utime.sleep(0.1)  # Pause pour éviter une mise à jour trop rapide


