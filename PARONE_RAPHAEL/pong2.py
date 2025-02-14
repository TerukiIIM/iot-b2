import machine
import ssd1306
import utime
import random

# Set up GPIO pin for input (single button)
button = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)  # Single button (GPIO13)

# Set up OLED screen
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Game variables
paddle_height = 14
paddle_width = 2
paddle_speed = 3
ball_radius = 2
ball_speed_x = 2
ball_speed_y = 1
player_score = 0
computer_score = 0
score_display_duration = 2  # Duration to display scores after reset (in seconds)

# Court variables
court_color = 1  # Court color (1 for white)
border_width = 2
court_line_width = 2
court_top = border_width
court_bottom = 64 - border_width

# Initial positions
player_paddle_y = (64 - paddle_height) // 2
computer_paddle_y = (64 - paddle_height) // 2
ball_pos_x = 64
ball_pos_y = 32

# Function to initialize the screen
def init_screen():
    oled.fill(0)  # Clear the screen
    oled.show()

# Function to draw the court
def draw_court():
    oled.fill_rect(0, 0, 128, border_width, court_color)  # Top border
    oled.fill_rect(0, 64 - border_width, 128, border_width, court_color)  # Bottom border
    oled.fill_rect(64 - court_line_width // 2, 0, court_line_width, 64, court_color)  # Middle line

# Function to draw paddles
def draw_paddle(x, y):
    oled.fill_rect(x, y, paddle_width, paddle_height, 1)

# Function to draw the player paddle
def draw_player_paddle():
    oled.fill_rect(0, player_paddle_y, paddle_width, paddle_height, 1)

# Function to update the player paddle's position based on button press
def update_player_paddle_position():
    global player_paddle_y
    if button.value() == 0 and player_paddle_y > court_top:  # Button pressed, move up
        player_paddle_y -= paddle_speed
    elif button.value() == 1 and player_paddle_y < court_bottom - paddle_height:  # Button released, move down
        player_paddle_y += paddle_speed

# Function to update the computer paddle's position (AI)
def update_computer_paddle_position():
    global computer_paddle_y
    delay = 4
    if computer_paddle_y < ball_pos_y - paddle_height // 2 and utime.ticks_ms() % delay == 0:
        computer_paddle_y += paddle_speed
    elif computer_paddle_y > ball_pos_y - paddle_height // 2 and utime.ticks_ms() % delay == 0:
        computer_paddle_y -= paddle_speed

# Function to draw the ball
def draw_ball():
    oled.fill_rect(int(ball_pos_x) - ball_radius, int(ball_pos_y) - ball_radius, int(ball_radius * 2), int(ball_radius * 2), 1)

# Function to update the ball's position and handle collisions
def update_ball_position():
    global ball_pos_x, ball_pos_y, ball_speed_x, ball_speed_y, player_score, computer_score

    # Erase previous ball position
    oled.fill_rect(int(ball_pos_x) - ball_radius, int(ball_pos_y) - ball_radius, int(ball_radius * 2), int(ball_radius * 2), 0)

    # Update ball position
    ball_pos_x += ball_speed_x
    ball_pos_y += ball_speed_y

    # Check for collisions with paddles
    if ball_pos_x - ball_radius <= paddle_width and player_paddle_y <= ball_pos_y <= player_paddle_y + paddle_height:
        if ball_speed_x < 0:
            ball_speed_x = abs(ball_speed_x)  # Reverse x direction
        ball_speed_y += random.uniform(-2, 2)  # Random angle adjustment

    elif ball_pos_x + ball_radius >= 128 - paddle_width and computer_paddle_y <= ball_pos_y <= computer_paddle_y + paddle_height:
        if ball_speed_x > 0:
            ball_speed_x = -abs(ball_speed_x)  # Reverse x direction
        ball_speed_y += random.uniform(-2, 2)  # Random angle adjustment

    # Check for collisions with top and bottom borders
    if ball_pos_y - ball_radius <= court_top:
        ball_speed_y = abs(ball_speed_y)  # Reverse y direction
        ball_pos_y = court_top + ball_radius
    elif ball_pos_y + ball_radius >= court_bottom:
        ball_speed_y = -abs(ball_speed_y)  # Reverse y direction
        ball_pos_y = court_bottom - ball_radius

    # Check for scoring
    if ball_pos_x - ball_radius <= 0:
        computer_score += 1
        reset_game(computer_serves=True)
    elif ball_pos_x + ball_radius >= 128:
        player_score += 1
        reset_game(computer_serves=False)

    # Draw the ball at the new position
    draw_ball()

# Function to reset the game after scoring
def reset_game(computer_serves):
    global ball_pos_x, ball_pos_y, ball_speed_x, ball_speed_y

    ball_pos_x = 64
    ball_pos_y = 32
    ball_speed_x = abs(ball_speed_x) if computer_serves else -abs(ball_speed_x)
    ball_speed_y = random.uniform(-2, 2)  # Randomize vertical speed

    # Display the scores for a short duration
    oled.fill(0)
    oled.text("Player: " + str(player_score), 38, 25, 1)
    oled.text("Computer: " + str(computer_score), 25, 35, 1)
    oled.show()
    utime.sleep(score_display_duration)

# Main game loop
def game_loop():
    while True:
        oled.fill(0)  # Clear the screen

        update_player_paddle_position()  # Update player paddle position
        update_computer_paddle_position()  # Update computer paddle position
        draw_court()  # Draw court
        draw_player_paddle()  # Draw player paddle
        draw_paddle(128 - paddle_width, computer_paddle_y)  # Draw computer paddle
        update_ball_position()  # Update ball position
        oled.show()  # Update display
        utime.sleep(0.01)

# Initialize the screen
init_screen()

# Start the game loop
game_loop()
