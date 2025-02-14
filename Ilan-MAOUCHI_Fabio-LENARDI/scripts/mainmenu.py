import time
import simon
import snake
import clock
import random
from machine import Pin, Timer

class LightShow:
    def start(self):
        simon.oled.fill(0)
        simon.oled.text("Light Show", 0, 0)
        simon.oled.show()
        
        for _ in range(3):
            simon.rainbow_animation(1)
            
            # Random sparkles
            for _ in range(50):
                led = random.randint(0, simon.NUM_LEDS-1)
                color = (random.randint(0,255), random.randint(0,255))
                simon.pixels_set(led, color)
                simon.pixels_show()
                time.sleep(0.05)
                simon.clear_leds()

class MainMenu:
    def __init__(self):
        self.apps = [
            ("Simon Game", simon.start_game),
            ("Snake Game", lambda: snake.start_snake_game(
                simon.oled, 
                simon.read_joystick, 
                lambda: simon.button1.value() == 0 and simon.button2.value() == 0,
                simon.read_button
            )),
            ("Light Show", self.light_show),
        ]
        self.current_selection = 0
        self.needs_redraw = True
        simon.init_simon()

    def light_show(self):
        simon.oled.fill(0)
        simon.oled.text("Light Show", 0, 0)
        simon.oled.show()
        
        for _ in range(3):
            simon.rainbow_animation(1)
            for _ in range(50):
                led = random.randint(0, simon.NUM_LEDS-1)
                color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                simon.pixels_set(led, color)
                simon.pixels_show()
                time.sleep(0.05)
                simon.clear_leds()

    def draw_menu(self):
        if not self.needs_redraw:
            return
            
        simon.oled.fill(0)
        simon.oled.text("Main Menu", 0, 0)
        simon.oled.text("-" * 16, 0, 10)
        
        for i, (app_name, _) in enumerate(self.apps):
            prefix = ">" if i == self.current_selection else " "
            simon.oled.text(f"{prefix}{app_name}", 0, 20 + i*10)
        
        simon.oled.show()
        self.needs_redraw = False

    def run(self):
        last_input = None
        
        while True:
            self.draw_menu()
            
            direction = simon.read_joystick()
            button = simon.read_button()
            
            if direction != last_input:
                if direction == "DOWN" and self.current_selection > 0:
                    self.current_selection -= 1
                    self.needs_redraw = True
                elif direction == "UP" and self.current_selection < len(self.apps) - 1:
                    self.current_selection += 1
                    self.needs_redraw = True
                
                if direction in ["UP", "DOWN"]:
                    if direction in simon.direction_leds:
                        simon.light_up_direction(simon.direction_leds[direction], simon.colors[direction])
                        time.sleep(0.1)
                        simon.clear_leds()
            
            if button in ["BTN1", "BTN2"] and not (simon.button1.value() == 0 and simon.button2.value() == 0):  # Accept either button but not both
                app_name, app_function = self.apps[self.current_selection]
                simon.oled.fill(0)
                simon.oled.text(f"Starting", 0, 0)
                simon.oled.text(app_name, 0, 20)
                simon.oled.show()
                time.sleep(1)
                
                app_function()
                
                simon.clear_leds()
                time.sleep(0.5)
                simon.init_simon()
                self.needs_redraw = True
            
            last_input = direction
            time.sleep(0.05)

if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
