import ssd1306
from machine import I2C, Pin

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

oled.fill(0)  # Remplir l'écran en noir
oled.show()

def display_text(message, line=0):
    # Efface complètement la ligne avec un rectangle noir
    oled.fill_rect(0, line * 11, 128, 11, 0)
    oled.text(message, 0, line * 11)
    oled.show()
    
    # Toujours afficher dans la console
    print(message)

def clear_line(line=0):
    oled.fill_rect(0, line * 11, 128, 11, 0)
    oled.show()

def clear_display():
    oled.fill(0)
    oled.show()