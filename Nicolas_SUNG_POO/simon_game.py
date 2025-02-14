import machine
import time
import random

led_pins = [14, 15, 16]
leds = [machine.Pin(pin, machine.Pin.OUT) for pin in led_pins]

button_pins = [17, 18, 19]
buttons = [machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_DOWN) for pin in button_pins]

# fonction pour allumer une LED
def flash_led(index, duration=0.5):
    leds[index].value(1)
    time.sleep(duration)
    leds[index].value(0)
    time.sleep(0.3)

# fonction pour attendre une pression de bouton
def wait_for_button():
    while True:
        for i, button in enumerate(buttons):
            if button.value() == 1: 
                time.sleep(0.2) 
                return i 

sequence = []
score = 0

print("Bienvenue dans le jeu du Simon !")
print("Appuyez sur les boutons 1 [Rouge], 2 [Jaune] et 3 [Bleu] pour reproduire la séquence.")

while True:
    sequence.append(random.randint(0, 2))
    
    print("Regardez bien la séquence...")
    for i in sequence:
        flash_led(i)
    
    print("Reproduisez la séquence en appuyant sur les bons boutons.")

    for i in sequence:
        pressed_button = wait_for_button() 

        if pressed_button != i:
            print("❌ Faux ! Vous avez perdu !")
            exit()  
        
        flash_led(pressed_button, 0.2)  

    time.sleep(1)  

    score += 1
    print(f"✅ Bien joué ! Score actuel : {score}\n")
