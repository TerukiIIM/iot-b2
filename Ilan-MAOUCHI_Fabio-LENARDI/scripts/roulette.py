import machine
import time
import random
import array
import rp2
import ssd1306
from time import sleep

# Pin definitions - Updated to match test.py
LED_PIN = 2  # Changed from 16 to 2
NUM_LEDS = 12
BRIGHTNESS = 0.25

# Joystick and button pins - Updated to match test.py
joystick_x = machine.ADC(27)  # Swapped from 26
joystick_y = machine.ADC(26)  # Swapped from 27
button1 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
button2 = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

# Joystick constants
MID = 32768
DEADZONE = 10000

# OLED Setup
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# LED Strip Setup
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

# Create the StateMachine with the ws2812 program, outputting on LED_PIN
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=machine.Pin(LED_PIN))
sm.active(1)

# Create array of LED values
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * BRIGHTNESS)
        g = int(((c >> 16) & 0xFF) * BRIGHTNESS)
        b = int((c & 0xFF) * BRIGHTNESS)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)

def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)

def clear_leds():
    pixels_fill((0, 0, 0))
    pixels_show()

def rainbow_animation(cycles=1):
    for _ in range(cycles):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS)
            pixels_set(i, wheel(rc_index & 255))
        pixels_show()
        time.sleep(0.05)

def wheel(pos):
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def fancy_startup_animation():
    """Enhanced startup animation with better timing and effects"""
    # Initial rainbow spin
    for j in range(2):  # Reduced rotations for faster startup
        for i in range(NUM_LEDS * 2):
            clear_leds()
            # Create trailing effect
            for k in range(3):  # Shorter trail for faster response
                pos = (i - k) % NUM_LEDS
                color = wheel(((i * 256 // NUM_LEDS) + k * 25) % 255)
                brightness = 1.0 - (k * 0.3)
                pixels_set(pos, tuple(int(c * brightness) for c in color))
            pixels_show()
            time.sleep(0.02)  # Faster animation
    
    # Color preview
    for color_name, color in ROULETTE_COLORS.items():
        pixels_fill(color)
        pixels_show()
        time.sleep(0.2)
    
    clear_leds()

# Roulette specific colors and constants
ROULETTE_COLORS = {
    "red": (255, 0, 0),
    "black": (50, 50, 50),
    "green": (0, 255, 0),
    "white": (255, 255, 255),
    "highlight": (255, 215, 0),  # Golden color for highlights
    "win": (0, 255, 0),          # Green for wins
    "lose": (255, 0, 0),         # Red for losses
}

# Betting options and payouts
BET_TYPES = {
    "single": 12,     # Reduced from 35 to 12 for better odds
    "color": 2,       # Red or Black (unchanged)
    "even_odd": 2,    # Even or Odd (unchanged)
    "dozen": 2,       # 1-4, 5-8, 9-12
    "half": 1.5,      # 1-6 or 7-12
    "adjacent": 6,    # New! Bet on a number and its neighbors
}

# Roulette segments (12 LEDs total)
SEGMENTS = {
    0: ("green", 0),     # Green 0
    1: ("red", 1),       # Red 1
    2: ("black", 2),     # Black 2
    3: ("red", 3),       # Red 3
    4: ("black", 4),     # Black 4
    5: ("red", 5),       # Red 5
    6: ("black", 6),     # Black 6
    7: ("red", 7),       # Red 7
    8: ("black", 8),     # Black 8
    9: ("red", 9),       # Red 9
    10: ("black", 10),   # Black 10
    11: ("red", 11),     # Red 11
}

def fisher_yates_shuffle(arr):
    """MicroPython compatible array shuffle"""
    n = len(arr)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

class LedRoulette:
    def __init__(self):
        self.balance = 1000
        self.current_bet = 100
        self.min_bet = 100
        self.max_bet = 1000
        self.spinning = False
        self.current_pos = 0
        self.speed = 0
        self.selected_color = "red"  # Current bet color
        self.button1_last = 1
        self.button2_last = 1
        self.button_cooldown = 0
        self.selected_position = 0  # Add selected position
        self.segments = SEGMENTS.copy()  # Store current segment layout
        self.last_joystick_action = None
        self.joystick_indicator_timer = 0
        self.message = ""
        self.message_timer = 0
        self.bet_type = "single"  # Default bet type
        self.last_positions = []  # Track last landing positions
        self.last_spin_time = 0
        self.last_display_time = 0  # Add this for display throttling
        self.last_update = time.ticks_ms()
        self.update_interval = 50  # Set fixed update interval (like in test.py)
        self.should_update = True  # Flag to control LED updates
        self.current_bet_info = {
            "type": "single",
            "color": None,
            "position": 0
        }  # Track current bet details
        random.seed(time.ticks_ms())  # Seed random with current time
        self.led_state_changed = True  # New flag to track if LEDs need updating
        self.last_wheel_state = None  # Track last wheel state to avoid unnecessary updates
        self.base_brightness = 0.1      # Dim for non-selected LEDs
        self.select_brightness = 0.8    # Bright for selected position
        self.spin_brightness = 1.0      # Full brightness during spin
        self.trail_brightness = 0.3     # Trail brightness during spin
    
    def show_balance(self):
        """Optimized OLED display with better text layout"""
        oled.fill(0)
        
        # Top row: Balance (right-aligned)
        balance_text = f"${self.balance}"
        balance_width = len(balance_text) * 8  # Assuming 8 pixels per character
        oled.text(balance_text, 128 - balance_width, 0)
        
        # Second row: Bet amount
        oled.text(f"Bet: ${self.current_bet}", 0, 16)
        
        # Third row: Position info (split into two lines if needed)
        pos_info = f"Pos {self.selected_position}"
        if self.bet_type != "single":
            pos_info = self.bet_type.upper()
        oled.text(pos_info, 0, 32)
        
        # Fourth row: Potential win
        potential = self.current_bet * self.get_payout()
        oled.text(f"Win: ${potential}", 0, 40)
        
        # Bottom rows: Messages or controls
        if time.ticks_diff(time.ticks_ms(), self.message_timer) < 2000:
            # Split message into two lines if needed
            words = self.message.split()
            line1 = ""
            line2 = ""
            for word in words:
                if len(line1 + " " + word) <= 16:  # Max 16 chars per line
                    line1 = (line1 + " " + word).strip()
                else:
                    line2 = (line2 + " " + word).strip()
            oled.text(line1, 0, 48)
            if line2:
                oled.text(line2, 0, 56)
        elif not self.spinning:
            oled.text("BTN1: Spin", 0, 48)
            oled.text("BTN2: Bet", 0, 56)
        
        # Show joystick action if recent
        if time.ticks_diff(time.ticks_ms(), self.joystick_indicator_timer) < 1000:
            # Small arrow indicator in top-left
            arrow = ">" if self.last_joystick_action == "RIGHT" else "<"
            oled.text(arrow, 0, 0)
        
        oled.show()

    def get_payout(self):
        """Calculate potential payout based on bet type"""
        if self.bet_type == "single":
            return BET_TYPES["single"]
        return BET_TYPES[self.bet_type]

    def check_win(self, landed_position):
        """Fixed win checking logic with proper color handling"""
        landed_number = self.segments[landed_position][1]
        landed_color = self.segments[landed_position][0]
        
        if self.current_bet_info["type"] == "color":
            won = landed_color == self.current_bet_info["color"]
            print(f"Bet color: {self.current_bet_info['color']}, Landed color: {landed_color}")
            return won
        
        if self.bet_type == "single":
            return landed_position == self.selected_position
        elif self.bet_type == "adjacent":
            return landed_position in [
                (self.selected_position - 1) % NUM_LEDS,
                self.selected_position,
                (self.selected_position + 1) % NUM_LEDS
            ]
        elif self.bet_type == "even_odd":
            is_even = landed_number % 2 == 0
            return (self.selected_position == 0 and is_even) or \
                   (self.selected_position == 1 and not is_even)
        elif self.bet_type == "dozen":
            if self.selected_position == 0:
                return 0 <= landed_number <= 4
            elif self.selected_position == 1:
                return 3 <= landed_number <= 8
            else:
                return 7 <= landed_number <= 11
        elif self.bet_type == "half":
            return (self.selected_position == 0 and landed_number <= 6) or \
                   (self.selected_position == 1 and landed_number >= 5)
        return False

    def update_message(self, msg):
        """Update display message with timer and optional split lines"""
        if len(msg) > 16:  # If message is too long, add natural line breaks
            words = msg.split()
            line1 = ""
            line2 = ""
            for word in words:
                if len(line1 + " " + word) <= 16:
                    line1 = (line1 + " " + word).strip()
                else:
                    line2 = (line2 + " " + word).strip()
            self.message = line1 + "\n" + line2
        else:
            self.message = msg
        self.message_timer = time.ticks_ms()
    
    def spin_animation(self):
        """Fixed spin animation with proper bet tracking"""
        self.spinning = True
        
        # Store current bet information
        if self.bet_type == "color":
            self.current_bet_info = {
                "type": "color",
                "color": self.selected_color,
                "position": None
            }
        else:
            self.current_bet_info = {
                "type": self.bet_type,
                "color": self.segments[self.selected_position][0],
                "position": self.selected_position
            }
        
        # Print current bet info
        print(f"\nBetting on: {self.current_bet_info['type']}")
        if self.current_bet_info["type"] == "color":
            print(f"Selected color: {self.current_bet_info['color']}")
        else:
            print(f"Position: {self.current_bet_info['position']} "
                  f"({self.segments[self.selected_position][0]} {self.segments[self.selected_position][1]})")
        print(f"Bet amount: ${self.current_bet}")
        print("Spinning...")
        
        # Initial rapid spin
        speed = 20
        decay = random.uniform(0.97, 0.99)
        current_position = float(self.current_pos)  # Convert to float for smooth animation
        
        # Add anticipation build-up
        for _ in range(3):
            pixels_fill(ROULETTE_COLORS["highlight"])
            pixels_show()
            time.sleep(0.1)
            clear_leds()
            time.sleep(0.1)
        
        # Spin until naturally stops
        min_rotations = 3  # Minimum number of full rotations
        rotations_done = 0
        
        while speed > 0.1 or rotations_done < min_rotations:
            # Read joystick for speed/direction control
            x_val = joystick_x.read_u16()
            x_offset = (x_val - MID) / MID
            
            # Update speed based on rotations
            if rotations_done < min_rotations:
                speed = max(15, speed + x_offset)  # Keep high speed for minimum rotations
            else:
                speed *= decay  # Start natural slowdown
                speed = max(0.1, speed + x_offset * 0.5)
            
            # Update position and track rotations
            prev_pos = int(current_position) % NUM_LEDS
            current_position += speed
            new_pos = int(current_position) % NUM_LEDS
            if new_pos < prev_pos:  # Completed a rotation
                rotations_done += 1
            
            self.current_pos = new_pos
            self.show_wheel()
            time.sleep(0.02)
        
        # Natural final position is where it stopped
        final_position = self.current_pos
        final_color = self.segments[final_position][0]
        final_number = self.segments[final_position][1]
        print(f"\nLanded on: Position {final_position}")
        print(f"Color: {final_color}")
        print(f"Number: {final_number}")
        
        # Calculate result based on where it actually landed
        if self.check_win(final_position):
            winnings = self.current_bet * self.get_payout()
            print(f"Winner! +${winnings}")
            self.balance += winnings
            self.show_win_animation(winnings)
        else:
            print(f"Lost ${self.current_bet}")
            self.balance -= self.current_bet
            self.show_lose_animation()
        
        print(f"Current balance: ${self.balance}\n")
        self.spinning = False
        self.led_state_changed = True  # Force LED update after spin
        self.last_wheel_state = None  # Reset wheel state to force update

    def show_wheel(self):
        """Optimized wheel display with minimal updates"""
        if not (self.spinning or self.led_state_changed):
            return
        
        current_time = time.ticks_ms()
        if not self.spinning and time.ticks_diff(current_time, self.last_update) < self.update_interval:
            return
        
        self.last_update = current_time
        self.led_state_changed = False
        
        # Create new LED state
        new_state = []
        for i in range(NUM_LEDS):
            color = ROULETTE_COLORS[self.segments[i][0]]
            brightness = self.base_brightness  # Default dim brightness
            
            # Make selected position much brighter
            if i == self.selected_position and not self.spinning:
                brightness = self.select_brightness
                # Optional: Add subtle pulse to selected position
                brightness *= 0.9 + 0.1 * ((time.ticks_ms() % 1000) / 1000)
            
            if self.spinning and i == self.current_pos:
                brightness = self.spin_brightness
                # Add trail only during spin
                trail_pos = (i - 1) % NUM_LEDS
                trail_color = ROULETTE_COLORS[self.segments[trail_pos][0]]
                new_state.append((i, tuple(int(c * brightness) for c in color)))
                new_state.append((trail_pos, tuple(int(c * self.trail_brightness) for c in trail_color)))
                continue
            
            new_state.append((i, tuple(int(c * brightness) for c in color)))
        
        # Only update if state changed
        if new_state != self.last_wheel_state:
            clear_leds()
            for pos, color in new_state:
                pixels_set(pos, color)
            pixels_show()
            self.last_wheel_state = new_state
            if self.spinning:
                time.sleep(0.01)

    def flash_winner(self, segment):
        """Flash winning segment"""
        color = ROULETTE_COLORS[SEGMENTS[segment][0]]
        for _ in range(5):
            clear_leds()
            time.sleep(0.1)
            pixels_set(segment, color)
            pixels_show()
            time.sleep(0.1)
    
    def show_win_animation(self, amount):
        """Enhanced win animation"""
        # Spiral effect
        for _ in range(2):
            for i in range(NUM_LEDS):
                clear_leds()
                for j in range(3):
                    pos = (i + j) % NUM_LEDS
                    pixels_set(pos, ROULETTE_COLORS["highlight"])  # Changed from "gold"
                pixels_show()
                time.sleep(0.05)
        
        # Victory message with amount won
        self.update_message(f"WIN! +${amount}")
        rainbow_animation(1)
        time.sleep(1)
    
    def show_lose_animation(self):
        """Show losing animation"""
        pixels_fill(ROULETTE_COLORS["lose"])  # Changed from "red"
        pixels_show()
        time.sleep(0.5)
        clear_leds()
        oled.fill(0)
        oled.text("Better luck", 0, 20)
        oled.text("next time!", 0, 40)
        oled.show()
        time.sleep(2)
    
    def change_bet(self):
        """Cycle through bet amounts"""
        bets = [100, 200, 500, 1000]
        current_index = bets.index(self.current_bet)
        self.current_bet = bets[(current_index + 1) % len(bets)]
    
    def change_color(self):
        """Fixed color selection with proper state tracking"""
        y_val = joystick_y.read_u16()
        old_color = self.selected_color
        
        if y_val < MID - DEADZONE:
            self.selected_color = "red"
        elif y_val > MID + DEADZONE:
            self.selected_color = "black"
        elif abs(y_val - MID) < DEADZONE:
            self.selected_color = "green"
        
        if old_color != self.selected_color:
            print(f"Selected color: {self.selected_color}")
            self.update_message(f"Selected: {self.selected_color}")
            self.current_bet_info["color"] = self.selected_color
            self.should_update = True

    def change_bet_type(self):
        """Cycle through different bet types"""
        old_type = self.bet_type
        bet_types = ["single", "adjacent", "color", "even_odd", "dozen", "half"]
        current_index = bet_types.index(self.bet_type)
        self.bet_type = bet_types[(current_index + 1) % len(bet_types)]
        
        if old_type != self.bet_type:
            print(f"\nBet type changed to: {self.bet_type}")
        
        # Show explanation of current bet type
        explanations = {
            "single": "Bet on exact number",
            "adjacent": "Win on number ±1",
            "color": "Bet on color",
            "even_odd": "Bet even/odd",
            "dozen": "Bet on range",
            "half": "Bet high/low"
        }
        self.update_message(f"{self.bet_type}: {explanations[self.bet_type]}")

    def check_buttons(self):
        """Improved button handling with debouncing"""
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.button_cooldown) < 200:
            return
        
        btn1 = button1.value()
        btn2 = button2.value()
        
        if btn1 == 0 and self.button1_last == 1:
            if button2.value() == 0:  # Both buttons pressed
                self.change_bet_type()
            else:
                self.spin_animation()
        elif btn2 == 0 and self.button2_last == 1:
            self.change_bet()
        
        self.button1_last = btn1
        self.button2_last = btn2

    def randomize_segments(self):
        """Randomize segment positions using MicroPython compatible method"""
        if time.ticks_diff(time.ticks_ms(), self.last_spin_time) > 10000:  # Only shuffle every 10 seconds
            positions = list(range(NUM_LEDS))
            fisher_yates_shuffle(positions)
            new_segments = {}
            for new_pos, old_pos in enumerate(positions):
                new_segments[new_pos] = SEGMENTS[old_pos]
            self.segments = new_segments
            self.last_spin_time = time.ticks_ms()
    
    def change_position(self):
        """Enhanced position selection with feedback"""
        x_val = joystick_x.read_u16()
        old_pos = self.selected_position
        
        if x_val < MID - DEADZONE:
            self.selected_position = (self.selected_position - 1) % NUM_LEDS
            self.last_joystick_action = "LEFT"
            self.joystick_indicator_timer = time.ticks_ms()
            self.led_state_changed = True  # Trigger LED update
        elif x_val > MID + DEADZONE:
            self.selected_position = (self.selected_position + 1) % NUM_LEDS
            self.last_joystick_action = "RIGHT"
            self.joystick_indicator_timer = time.ticks_ms()
            self.led_state_changed = True  # Trigger LED update
        
        # Print selection changes
        if old_pos != self.selected_position:
            pos_color = self.segments[self.selected_position][0]
            pos_number = self.segments[self.selected_position][1]
            print(f"Selected: Position {self.selected_position} ({pos_color} {pos_number})")
            self.update_message(f"Selected: {pos_color}")
        
        time.sleep(0.1)  # Add small delay for smoother selection

def main():
    game = LedRoulette()
    fancy_startup_animation()
    game.update_message("Welcome to Roulette!")
    game.randomize_segments()  # Initial randomization
    
    while True:
        if game.balance < game.min_bet:
            oled.fill(0)
            oled.text("Game Over!", 0, 20)
            oled.text(f"Final: ${game.balance}", 0, 40)
            oled.show()
            pixels_fill(ROULETTE_COLORS["lose"])  # Changed from "red"
            pixels_show()  # Added missing pixels_show()
            time.sleep(2)
            
            # Randomize wheel for next game
            game.randomize_segments()
            break
            
        if game.led_state_changed or game.spinning:
            game.show_wheel()  # Only update wheel when needed
        
        game.show_balance()
        
        if not game.spinning:
            game.check_buttons()  # New button checking method
            game.change_position()  # Check for position changes
        
        time.sleep(0.01)

if __name__ == "__main__":
    main()
