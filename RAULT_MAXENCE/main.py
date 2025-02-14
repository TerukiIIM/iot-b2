from machine import Pin, SoftI2C, PWM
from pico_i2c_lcd import I2cLcd
from time import sleep

# Configuration de l'ecran LCD
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = SoftI2C(sda=Pin(14), scl=Pin(27), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
lcd.clear()
lcd.putstr("Minuteur Pret")
sleep(2)
lcd.clear()

# Configuration des boutons
btn_start_pause = Pin(2, Pin.IN, Pin.PULL_UP)
btn_add_30s = Pin(3, Pin.IN, Pin.PULL_UP)
btn_remove_30s = Pin(4, Pin.IN, Pin.PULL_UP)
btn_melody = Pin(5, Pin.IN, Pin.PULL_UP)

# Configuration du buzzer sur GP16
buzzer = PWM(Pin(16))
buzzer.duty_u16(0)  

# Variables globales
timer_seconds = 0
running = False
melody_choice = 0

melodies = [
    [(262, 0.4), (330, 0.4), (392, 0.4), (523, 0.6), (660, 0.6), (784, 0.6)],  # Classique
    [(440, 0.3), (440, 0.3), (440, 0.3), (349, 0.5), (392, 0.5), (330, 0.4), (262, 0.4)],  # Gag
    [(523, 0.3), (494, 0.3), (523, 0.3), (587, 0.5), (523, 0.5), (660, 0.4), (784, 0.4)],  # Alarme
]

def play_tone(freq, duration):
    buzzer.freq(freq)
    buzzer.duty_u16(20000)
    sleep(duration)
    buzzer.duty_u16(0)
    sleep(0.1)

def play_melody():
    for freq, duration in melodies[melody_choice]:
        play_tone(freq, duration)
        sleep(0.1)

def update_display():
    lcd.clear()
    minutes = timer_seconds // 60
    seconds = timer_seconds % 60
    lcd.putstr(f"Temps: {minutes:02}:{seconds:02}")

def handle_buttons():
    global timer_seconds, running, melody_choice
    
    if not btn_start_pause.value():
        running = not running
        lcd.clear()
        lcd.putstr("En cours..." if running else "Pause")
        print("Etat: En cours" if running else "Etat: Pause")
        sleep(0.5)
        while not btn_start_pause.value():  # Attendre le relachement du bouton
            sleep(0.1)
    
    if not btn_add_30s.value():
        timer_seconds += 30
        update_display()
        print(f"Temps ajoute: {timer_seconds} secondes")
        sleep(0.5)
    
    if not btn_remove_30s.value():
        timer_seconds = max(0, timer_seconds - 30)
        update_display()
        print(f"Temps retire: {timer_seconds} secondes")
        sleep(0.5)
    
    if not btn_melody.value():
        melody_choice = (melody_choice + 1) % len(melodies)
        lcd.clear()
        lcd.putstr(f"Melodie {melody_choice+1}")
        print(f"Melodie changee: {melody_choice+1}")
        sleep(0.5)
        while not btn_melody.value():  
            sleep(0.1)

def run_timer():
    global timer_seconds, running
    while True:
        handle_buttons()
        if running and timer_seconds > 0:
            sleep(1)
            timer_seconds -= 1
            update_display()
            print(f"Temps restant: {timer_seconds} secondes")
            while not running:
                handle_buttons()
                sleep(0.1)
            if timer_seconds == 0:
                lcd.clear()
                lcd.putstr("Temps ecoule!")
                print("Temps ecoule!")
                play_melody()
                sleep(2)
                lcd.clear()
                lcd.putstr("Minuteur Pret")
                running = False
        sleep(0.1)

try:
    run_timer()
except KeyboardInterrupt:
    lcd.clear()
    lcd.putstr("Au revoir")
    print("Programme arrete.")
