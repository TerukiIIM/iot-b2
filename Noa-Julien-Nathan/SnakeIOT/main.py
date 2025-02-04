from machine import I2C, Pin
from ssd1306 import SSD1306_I2C
import time
import random

# Configuration de l'écran OLED
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Configuration des boutons
BTN_START = Pin(15, Pin.IN, Pin.PULL_UP)  # Bouton Start
BTN_UP = Pin(14, Pin.IN, Pin.PULL_UP)     # Bouton Haut
BTN_DOWN = Pin(16, Pin.IN, Pin.PULL_UP)   # Bouton Bas
BTN_LEFT = Pin(12, Pin.IN, Pin.PULL_UP)   # Bouton Gauche
BTN_RIGHT = Pin(11, Pin.IN, Pin.PULL_UP)  # Bouton Droite

# Variables du jeu
BLOCK_SIZE = 4
snake = [(32, 32)]  
direction = (1, 0)  
food = (random.randrange(0, oled_width, BLOCK_SIZE),
        random.randrange(0, oled_height, BLOCK_SIZE))
game_over = False
game_started = False
score = 0

def draw_block(x, y):
    oled.fill_rect(x, y, BLOCK_SIZE, BLOCK_SIZE, 1)

def handle_input():
    global direction
    if not BTN_UP.value():
        direction = (0, -1)
    elif not BTN_DOWN.value():
        direction = (0, 1)
    elif not BTN_LEFT.value():
        direction = (-1, 0)
    elif not BTN_RIGHT.value():
        direction = (1, 0)

def check_collision():
    head = snake[0]
    # Vérifier les collisions avec les murs
    if (head[0] < 0 or head[0] >= oled_width or
        head[1] < 0 or head[1] >= oled_height):
        return True
    # Vérifier les collisions avec le corps du serpent
    if head in snake[1:]:
        return True
    return False

def game_loop():
    global food, game_over, snake, score
    
    while not game_over:
        oled.fill(0) 
        
        # Afficher le score en haut
        oled.text(f"Score:{score}", 0, 0)
        
        # Gérer les entrées
        handle_input()
        
        # Mettre à jour la position du serpent
        new_head = (snake[0][0] + direction[0] * BLOCK_SIZE,
                   snake[0][1] + direction[1] * BLOCK_SIZE)
        snake.insert(0, new_head)
        
        # Vérifier si le serpent mange la nourriture
        if abs(snake[0][0] - food[0]) < BLOCK_SIZE and abs(snake[0][1] - food[1]) < BLOCK_SIZE:
            food = (random.randrange(0, oled_width, BLOCK_SIZE),
                   random.randrange(0, oled_height, BLOCK_SIZE))
            score += 1  
        else:
            snake.pop()
        
        # Vérifier les collisions
        if check_collision():
            game_over = True
            break
        
        # Dessiner le serpent
        for segment in snake:
            draw_block(segment[0], segment[1])
        
        # Dessiner la nourriture
        draw_block(food[0], food[1])
        
        oled.show()
        time.sleep(0.1)
        
        


# Boucle principale
while True:
    if not game_started:
        oled.fill(0)
        oled.text("SNAKE GAME", 20, 20)
        oled.text("Press START", 20, 40)
        oled.show()
        
        if not BTN_START.value():
            game_started = True
            game_over = False
            snake = [(32, 32)]
            direction = (1, 0)
            score = 0  
            food = (random.randrange(0, oled_width, BLOCK_SIZE),
                   random.randrange(0, oled_height, BLOCK_SIZE))
            game_loop()
    
    if game_over:
        oled.fill(0)
        oled.text("GAME OVER", 20, 20)
        oled.text(f"Score: {score}", 20, 30)  
        oled.text("Press START", 20, 40)
        oled.show()
        game_started = False
        while BTN_START.value():
            time.sleep(0.1)
