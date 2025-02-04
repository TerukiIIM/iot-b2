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

# Colors
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# Lists
color_list = [red, blue, green]
led_list = [led_A, led_B, led_C, led_D, led_E]
btn_list = [btn_A, btn_B, btn_C, btn_D, btn_E]

#endregion



#region Difficulty()

# Here will go all the difficulty related functions

#endregion



#region Start()

def start_game():
    # Check the score
    if score > best_score:
        best_score = score

    # Show the starting menu
    oled.fill(0)
    screen.text('Best Score : ' + str(best_score), 0, 0)
    screen.text('Last Score : ' + str(score), 0, 10)
    screen.text('Press any button', 0, 30)
    screen.text('To START !', 0, 40)
    screen.show()

    # Reset the variable
    patern = []
    score = 0
    chain = init_chain

    # Start the game when a button is pressed
    for btn in range(btn_list):
        # Wait for in input
        input() # A vérifier parce que je suis vraiment pas sûr de moi
        if btn.value() == 1:
        testSimon1(5)

#endregion



#region Light()

def light_patern():
    for x in range(chain):
        # Clear all leds
        leds.clear()

        # Define a led
        led_r = random.randrange(0, len(led_list))
        # Save this led in a list
        patern.append(led_r)
        # Set up the led
        leds.set_pixel(led_list[led_r], blue)

        # Show the led
        leds.show()

        # Wait 0.5s
        time.sleep(0.5)

        # Clear the led
        leds.clear()
        leds.show()

        # Wait 0.75s
        time.sleep(0.75)
    # Next step of the game
    check_patern()

#endregion


#region Check()

def check_patern():
    for x in range(patern):
        # Wait for in input
        input() # A vérifier parce que je suis vraiment pas sûr de moi

        # If it's the right button, add score
        if btn_list[x].value() == 1:
            score += 1
        # If it's not the right button, start a new game
        else:
            start_game()
    
    # New round
    chain += 1
    light_patern()

#endregion



#region Exec

start_game()

#endregion
