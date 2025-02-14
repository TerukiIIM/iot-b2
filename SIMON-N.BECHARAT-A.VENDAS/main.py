#region Import

# Globals
from machine import Pin, SoftI2C
# Screen manager
import ssd1306
# Leds manager
from neopixel import Neopixel
# Used for the algorithmy
import time
import random

#endregion



#region Set Pins

# Screen
screen_pin = SoftI2C(scl=Pin(9), sda=Pin(8))

# Buttons
btn_A = Pin(15, Pin.IN, Pin.PULL_DOWN)
btn_B = Pin(14, Pin.IN, Pin.PULL_DOWN)
btn_C = Pin(13, Pin.IN, Pin.PULL_DOWN)
btn_D = Pin(12, Pin.IN, Pin.PULL_DOWN)
btn_E = Pin(3, Pin.IN, Pin.PULL_DOWN)

# Leds
led_pin = 20

#endregion



#region Leds params

num_leds = 12
leds = Neopixel(num_leds, 0, led_pin)
leds.brightness(5)

led_A = 2
led_B = 4
led_C = 6
led_D = 8
led_E = 10

#endregion



#region Screen params

screen_width = 128
screen_height = 64
screen = ssd1306.SSD1306_I2C(screen_width, screen_height, screen_pin)

#endregion



#region Variables

# Score
patern = []
best_score = 0
score = 0
init_chain = 5
chain = 0

# Lists
btn_list = [btn_A, btn_B, btn_C, btn_D, btn_E]
led_list = [led_A, led_B, led_C, led_D, led_E]

#endregion



#region Start()

def start_game():
    screen.fill(0)  # Clear the screen
    global score, best_score, patern, chain, init_chain, btn_list
    # Check the score
    if score > best_score:
        best_score = score

    # Show the starting menu
    screen.text('Best Score : ' + str(best_score), 0, 0)
    screen.text('Last Score : ' + str(score), 0, 10)
    # screen.text('Press any button to START!', 0, 30)
    screen.show()

    # Reset the variable
    patern = []
    chain = init_chain

    # Start the game when a button is pressed
    # input("Press Enter to start...")
    light_patern(chain, btn_list)

#endregion



#region Light()

def light_patern(chain, btn_list):
    global patern
    patern = []  # Reset the patern for the new game
    for x in range(chain):
        # Define a led
        led_r = random.randrange(len(led_list))
        # Save this led in a list
        patern.append(led_r)
        # Show the led
        leds.set_pixel(led_list[led_r], (0, 0, 255))
        leds.show()
        time.sleep(0.5)
        leds.clear()
        leds.show()
        time.sleep(0.75)
    # Next step of the game
    update_screen("It's your turn !")
    check_patern(patern, btn_list)

#endregion

def update_screen(text_params) :
    screen.fill(0)  # Clear the screen
    screen.text('Best Score : ' + str(best_score), 0, 0)
    screen.text('Last Score : ' + str(score), 0, 10)
    screen.text(text_params, 0, 30)
    screen.show()

def restart_game():
    global score, best_score, patern, chain, init_chain
    time.sleep(2) 
    start_game()

def game_over():
    global score, best_score, patern, chain, init_chain
    if score > best_score:
        best_score = score
    score = 0
    update_screen("Game Over!")
    time.sleep(2)  # Laisser le temps de voir la fin du jeu
    start_game()

def check_patern(patern, btn_list):
    global score, chain
    for expected_led in patern:
        # Attente d'un appui sur un bouton
        pressed = False
        btn_pressed = False
        while not pressed:
            if btn_list[0].value() :
                user_input = btn_list[0]
                btn_pressed = True
            if btn_list[1].value() :
                user_input = btn_list[1]
                btn_pressed = True
            if btn_list[2].value() :
                user_input = btn_list[2]
                btn_pressed = True
            if btn_list[3].value() :
                user_input = btn_list[3]
                btn_pressed = True
            if btn_list[4].value() :
                user_input = btn_list[4]
                btn_pressed = True
            if btn_pressed == True :
                if user_input in btn_list:
                    pressed = True
                    time.sleep(0.5)
                    if btn_list.index(user_input) == expected_led:
                        leds.set_pixel(led_list[expected_led], (255, 0, 0))
                        leds.show()
                        time.sleep(0.5)
                        leds.clear()
                        leds.show()
                        score += 1
                        update_screen("")
                    else:
                        leds.set_pixel(led_list[expected_led], (0, 0, 255))
                        leds.set_pixel(led_list[btn_list.index(user_input)], (0, 255, 0))
                        leds.show()
                        time.sleep(1)
                        leds.clear()
                        leds.show()
                        game_over()
                        return
            time.sleep(0.1)  # Petite pause pour éviter une détection multiple

    # Nouveau tour
    update_screen("Good job!")
    chain += 1
    time.sleep(1)
    restart_game()

#region Exec

start_game()

#endregion

