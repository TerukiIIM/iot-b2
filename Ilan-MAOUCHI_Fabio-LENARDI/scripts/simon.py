import machine
import time
import random
import array
import rp2
import ssd1306
from time import sleep

# Pin configuration
joystick_x_pin = 27
joystick_y_pin = 26
button1_pin = 14
button2_pin = 15
led_ring_pin = 2

# Joystick setup
joystick_x = machine.ADC(joystick_x_pin)
joystick_y = machine.ADC(joystick_y_pin)
MID = 32500  # Middle value for the joystick
DEADZONE = 7777

# Button setup
button1 = machine.Pin(button1_pin, machine.Pin.IN, machine.Pin.PULL_UP)
button2 = machine.Pin(button2_pin, machine.Pin.IN, machine.Pin.PULL_UP)

# LED ring setup
NUM_LEDS = 12
brightness = 0.1

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

# Initialize the LED ring
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=machine.Pin(led_ring_pin))
sm.active(1)
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

# LED helper functions
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i, c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g << 16) + (r << 8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)

def pixels_set(i, color):
    ar[i] = (color[1] << 16) + (color[0] << 8) + color[2]

def pixels_fill(color):
    for i in range(NUM_LEDS):
        pixels_set(i, color)
    pixels_show()

def clear_leds():
    pixels_fill((0, 0, 0))

# Simplified direction mapping
direction_leds = {
    "UP": 6,
    "RIGHT": 9,
    "DOWN": 0,
    "LEFT": 3
}

# Enhanced color palette with unique colors for each direction
colors = {
    "BTN1": (255, 0, 0),          # Pure Red
    "BTN2": (0, 0, 255),          # Pure Blue
    "UP": (0, 255, 0),            # Green
    "DOWN": (0, 255, 255),        # Cyan
    "LEFT": (255, 0, 255),        # Magenta
    "RIGHT": (255, 255, 0),       # Yellow
    "success": (0, 255, 0),       # Green
    "failure": (255, 0, 0),       # Red
    "countdown": (128, 128, 128), # Dim white
    "waiting": (30, 30, 30),      # Dim white
    "progress": (0, 100, 0),      # Dim green
    "off": (0, 0, 0),             # Off
    "rainbow": [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (75, 0, 130),   # Indigo
        (148, 0, 211)   # Violet
    ]
}

# Add game difficulty constants
BASE_SEQUENCE_TIME = 1.2  # Base time to show each sequence step
BASE_PAUSE_TIME = 0.4    # Base pause time between steps
BASE_INPUT_TIME = 10.0   # Base time for user input
MIN_TIME_LIMIT = 3.0     # Minimum time limit for inputs
MAX_SPEED_MULTIPLIER = 3.0  # Maximum speed increase

def get_speed_multiplier(sequence_length):
    """Calculate speed multiplier based on sequence length."""
    # Increase speed by 20% for each level after 2
    multiplier = 1.0 + ((sequence_length - 2) * 0.2)
    return min(MAX_SPEED_MULTIPLIER, multiplier)

def get_sequence_timings(sequence_length):
    """Get display and pause times based on current level."""
    speed_mult = get_speed_multiplier(sequence_length)
    display_time = BASE_SEQUENCE_TIME / speed_mult
    pause_time = BASE_PAUSE_TIME / speed_mult
    return display_time, pause_time

def get_input_time_limit(sequence_length):
    """Calculate time limit for inputs based on sequence length."""
    # Reduce time by 0.5s per level, minimum 3 seconds
    return max(MIN_TIME_LIMIT, BASE_INPUT_TIME - (sequence_length - 2) * 0.5)

# OLED display setup
i2c = machine.SoftI2C(scl=machine.Pin(1), sda=machine.Pin(0))

pin = machine.Pin(16, machine.Pin.OUT)
pin.value(0)  # Set GPIO16 low to reset OLED
time.sleep(0.1)  # Short delay to ensure reset
pin.value(1)  # Set GPIO16 high while OLED is running

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Add icons (8x8 pixels each) as byte arrays
HEART_ICON = bytearray([
    0b00100100,
    0b01111110,
    0b01111110,
    0b01111110,
    0b00111100,
    0b00011000,
    0b00000000,
    0b00000000,
])

TROPHY_ICON = bytearray([
    0b00111100,
    0b01111110,
    0b01111110,
    0b00011000,
    0b00011000,
    0b00111100,
    0b00000000,
    0b00000000,
])

STEPS_ICON = bytearray([
    0b00011000,
    0b00111100,
    0b01111110,
    0b00011000,
    0b00011000,
    0b00011000,
    0b00000000,
    0b00000000,
])

CLOCK_ICON = bytearray([
    0b00111100,
    0b01000010,
    0b10011001,
    0b10100001,
    0b10000001,
    0b01000010,
    0b00111100,
    0b00000000,
])

def draw_icon(icon, x, y):
    """Draw an 8x8 icon at the specified position."""
    for row in range(8):
        mask = 0x80
        for col in range(8):
            if icon[row] & mask:
                oled.pixel(x + col, y + row, 1)
            mask >>= 1

def format_message(message, start_y=32):
    """Split message into multiple lines if needed."""
    words = message.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) > 16:  # Max 16 chars per line
            lines.append(current_line)
            current_line = word
        else:
            current_line = (current_line + " " + word).strip()
    
    if current_line:
        lines.append(current_line)
    
    return lines

def update_display(lives, score, sequence_length, message="", time_left=None, difficulty=None):
    """Update the OLED display with enhanced information."""
    oled.fill(0)
    
    # Draw icons and their values
    draw_icon(HEART_ICON, 0, 0)
    oled.text(f'x{lives}', 10, 0)
    
    draw_icon(TROPHY_ICON, 35, 0)
    oled.text(f'{score}', 45, 0)
    
    # Show speed multiplier and difficulty
    speed_mult = get_speed_multiplier(sequence_length)
    oled.text(f'{speed_mult:.1f}x', 70, 0)
    
    # Draw time left if provided
    if time_left is not None:
        draw_icon(CLOCK_ICON, 0, 16)
        oled.text(f'{time_left:.1f}s', 10, 16)
        time_limit = get_input_time_limit(sequence_length)
        oled.text(f'/{time_limit:.1f}s', 45, 16)
    
    # Show difficulty level
   
    
    # Format and display message
    if message:
        lines = format_message(message)
        for i, line in enumerate(lines):
            oled.text(line, 0, 32 + i * 10)
    
    oled.show()

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def rainbow_animation(cycles=2):
    """Display a smooth rainbow animation."""
    for j in range(cycles * 255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS + j) & 255
            pixels_set(i, wheel(rc_index))
        pixels_show()
        time.sleep(0.01)

def fancy_startup_animation():
    """Display an enhanced startup animation sequence."""
    # Rainbow spin
    for _ in range(3):
        for j in range(len(colors["rainbow"])):
            for i in range(NUM_LEDS):
                color_idx = (i + j) % len(colors["rainbow"])
                pixels_set(i, colors["rainbow"][color_idx])
            pixels_show()
            time.sleep(0.05)
    
    # Converging lines
    for i in range(NUM_LEDS // 2):
        clear_leds()
        pixels_set(i, (255, 255, 255))
        pixels_set(NUM_LEDS - 1 - i, (255, 255, 255))
        pixels_show()
        time.sleep(0.05)
    
    # Direction preview
    for direction in ["UP", "RIGHT", "DOWN", "LEFT"]:
        if direction in direction_leds:
            light_up_direction(direction_leds[direction], colors[direction])
            time.sleep(0.3)
    clear_leds()

# Simplified inputs list
inputs = ["UP", "DOWN", "LEFT", "RIGHT", "BTN1", "BTN2"]

# Input detection
def read_joystick():
    x_val = joystick_x.read_u16()
    y_val = joystick_y.read_u16()
    
    # More lenient deadzone
    if abs(x_val - MID) < DEADZONE * 1.5 and abs(y_val - MID) < DEADZONE * 1.5:
        return None
    
    # Determine dominant direction
    x_offset = x_val - MID
    y_offset = y_val - MID
    
    # Use absolute values to determine which axis has larger movement
    if abs(x_offset) > abs(y_offset):
        if x_val < MID - DEADZONE:
            return "RIGHT"
        elif x_val > MID + DEADZONE:
            return "LEFT"
    else:
        if y_val < MID - DEADZONE:
            return "DOWN"
        elif y_val > MID + DEADZONE:
            return "UP"
    
    return None

def read_button():
    if button1.value() == 0:
        return "BTN1"
    if button2.value() == 0:
        return "BTN2"
    return None

# Game functions
def display_sequence(sequence, sequence_length):
    """Displays the Simon Says sequence on the LED ring with dynamic speed."""
    clear_leds()
    time.sleep(1)  # Initial pause
    
    display_time, pause_time = get_sequence_timings(sequence_length)
    
    for move in sequence:
        if check_menu_return():  # Add menu return check
            return False
        if move in direction_leds:  # Joystick directions
            light_up_direction(direction_leds[move], colors[move])
        elif move in colors:  # Button presses
            pixels_fill(colors[move])
            pixels_show()
        time.sleep(display_time)
        clear_leds()
        time.sleep(pause_time)
    return True

def light_up_direction(base_index, color):
    """Lights up LEDs for the indicated direction."""
    clear_leds()
    # Light up main LED and adjacent LEDs
    pixels_set(base_index, color)
    pixels_set((base_index + 1) % NUM_LEDS, tuple(c//2 for c in color))
    pixels_set((base_index - 1) % NUM_LEDS, tuple(c//2 for c in color))
    pixels_show()

def show_progress_indicator(current_step, total_steps):
    """Shows progress in sequence using dim LEDs."""
    for i in range(total_steps):
        if i < current_step:
            pixels_set(i, colors["progress"])
        else:
            pixels_set(i, colors["waiting"])
    pixels_show()

def show_smooth_countdown(seconds, total_time=10.0):
    """Display a smoother, more accurate countdown using white LEDs."""
    remaining_ratio = max(seconds / total_time, 0)  # Ensure non-negative
    leds_remaining = NUM_LEDS * remaining_ratio
    
    # Calculate full and partial LEDs
    full_leds = int(leds_remaining)
    partial = leds_remaining - full_leds
    
    # Only update countdown LEDs without clearing all LEDs to reduce flashing
    # Optionally, fill non-countdown LEDs with their current color or keep them off
    for i in range(NUM_LEDS):
        if i < full_leds:
            pixels_set(NUM_LEDS - 1 - i, colors["countdown"])
        elif i == full_leds and partial > 0:
            dim_white = tuple(int(c * partial * 0.5) for c in colors["countdown"])  # Further dimmed
            pixels_set(NUM_LEDS - 1 - i, dim_white)
        else:
            # Optionally maintain other LEDs' states or keep them off
            pass  # No operation to leave other LEDs unchanged
    
    pixels_show()

def get_user_input(sequence, lives, score, sequence_length):
    """Get user inputs with dynamic timing based on difficulty."""
    user_inputs = []
    joystick_centered = True
    last_input = None
    
    # Calculate time limit based on sequence length
    TOTAL_TIME = get_input_time_limit(sequence_length)
    
    time.sleep(0.5)
    clear_leds()

    for step in range(len(sequence)):
        start_time = time.ticks_ms()
        end_time = time.ticks_add(start_time, int(TOTAL_TIME * 1000))
        correct_move = sequence[step]
        input_received = False

        while time.ticks_diff(time.ticks_ms(), end_time) < 0 and not input_received:
            if check_menu_return():  # Add menu return check
                return ["MENU"]
            current_time = time.ticks_ms()
            remaining_ticks = time.ticks_diff(end_time, current_time)
            remaining = remaining_ticks / 1000.0

            # Update displays with enhanced information
            show_smooth_countdown(remaining, TOTAL_TIME)
            speed_mult = get_speed_multiplier(sequence_length)
            update_display(lives, score, sequence_length,
                         f"Your turn! ({step+1}/{len(sequence)})",
                         time_left=remaining,
                         difficulty=sequence_length-1)

            # Read input
            current_move = read_joystick() or read_button()

            # Process input
            if current_move is None:
                joystick_centered = True
                last_input = None  # Reset last_input when centered
            elif joystick_centered:
                if current_move == correct_move and current_move != last_input:
                    # Show correct input feedback
                    if current_move in direction_leds:
                        light_up_direction(direction_leds[current_move], colors[current_move])
                    else:
                        pixels_fill(colors[current_move])
                    pixels_show()
                    time.sleep(0.2)
                    clear_leds()
                    user_inputs.append(current_move)
                    last_input = current_move  # Update last input
                    joystick_centered = False  # Prevent further inputs until centered
                    input_received = True
                elif current_move == correct_move and current_move == last_input:
                    # Ignore duplicate input
                    pass
                else:
                    # Wrong input feedback
                    pixels_fill(colors["failure"])
                    time.sleep(0.2)
                    clear_leds()
                    return ["WRONG"]

            # Small delay to prevent CPU overload
            time.sleep(0.01)

        # Check if time ran out
        if not input_received:
            pixels_fill(colors["failure"])
            time.sleep(0.2)
            clear_leds()
            return ["TIMEOUT"]

    return user_inputs

def check_sequence(sequence, user_inputs):
    return sequence == user_inputs

# Add at the top with other functions
def check_menu_return():
    """Check if both buttons are pressed to return to menu"""
    return button1.value() == 0 and button2.value() == 0

# Modify start_game() function to allow menu return
def start_game():
    """Main game loop with dynamic difficulty."""
    clear_leds()
    fancy_startup_animation()
    
    lives = 3
    sequence_length = 2
    score = 0
    
    # Initial display update
    update_display(lives, score, sequence_length, "Get Ready!")
    sleep(2)
    
    while lives > 0:
        if check_menu_return():
            return
        # Update display with difficulty level
        update_display(lives, score, sequence_length, "Watch sequence", 
                      difficulty=sequence_length-1)
        
        # Generate sequence
        sequence = []
        for _ in range(sequence_length):
            if random.random() < 0.7:
                sequence.append(random.choice(["UP", "DOWN", "LEFT", "RIGHT"]))
            else:
                sequence.append(random.choice(["BTN1", "BTN2"]))
        
        # Show sequence with dynamic speed
        speed_mult = get_speed_multiplier(sequence_length)
        display_time, pause_time = get_sequence_timings(sequence_length)  # Get timing values
        update_display(lives, score, sequence_length,
                      f"Watch ({speed_mult:.1f}x speed)",
                      difficulty=sequence_length-1)
        
        if not display_sequence(sequence, sequence_length):  # Check return value
            return
        
        # Get user input with dynamic time limit
        time_limit = get_input_time_limit(sequence_length)
        update_display(lives, score, sequence_length,
                      f"Ready! {time_limit:.1f}s per move")
        user_inputs = get_user_input(sequence, lives, score, sequence_length)
        if user_inputs == ["MENU"] or check_menu_return():
            return
        
        # Check result
        if user_inputs == ["WRONG"]:
            print("Incorrect!")  # Optional: Can be removed or kept for debugging
            update_display(lives, score, sequence_length, "Incorrect!")
            lives -= 1
            pixels_fill(colors["failure"])
            sleep(0.5)
            sequence_length = max(2, sequence_length - 1)
        elif user_inputs == ["TIMEOUT"]:
            print("Time's up!")  # Optional: Can be removed or kept for debugging
            update_display(lives, score, sequence_length, "Time's up!")
            lives -= 1
            pixels_fill(colors["failure"])
            sleep(0.5)
            sequence_length = max(2, sequence_length - 1)
        elif len(user_inputs) == len(sequence):
            print("Correct!")  # Optional: Can be removed or kept for debugging
            update_display(lives, score, sequence_length, "Correct!")
            score += sequence_length
            pixels_fill(colors["success"])
            sleep(0.3)
            if score >= sequence_length * 2:
                sequence_length += 1
        
        clear_leds()
        time.sleep(0.5)
    
    # Game over sequence
    print(f"Game Over! Final Score: {score}")  # Optional: Can be removed or kept for debugging
    update_display(lives, score, sequence_length, f"Game Over!\nScore: {score}")
    pixels_fill(colors["failure"])
    sleep(10)
    clear_leds()
    oled.poweroff()  # Turn off OLED when the game ends

def init_simon():
    """Initialize simon game hardware."""
    global sm, oled
    # Initialize LED ring
    sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=machine.Pin(led_ring_pin))
    sm.active(1)
    
    # Initialize OLED
    i2c = machine.SoftI2C(scl=machine.Pin(1), sda=machine.Pin(0))
    pin = machine.Pin(16, machine.Pin.OUT)
    pin.value(0)
    time.sleep(0.1)
    pin.value(1)
    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

if __name__ == "__main__":
    init_simon()
    start_game()


