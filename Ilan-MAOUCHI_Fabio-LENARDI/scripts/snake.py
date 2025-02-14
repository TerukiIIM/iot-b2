import random
import time

class SnakeGame:
    def __init__(self, oled):
        self.oled = oled
        self.width = 128
        self.height = 64
        self.score_height = 15     # Visual score area height
        self.play_margin = 17     # Actual gameplay restriction
        self.block_size = 4
        self.reset_game()

    def reset_game(self):
        # Start snake in playable area below restricted zone
        start_y = (self.play_margin // self.block_size) + 1
        self.snake = [(4, start_y), (3, start_y), (2, start_y)]
        self.direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.base_speed = 0.08  # Slower base speed (about 12 moves per second)
        self.speed = self.base_speed
        
    def spawn_food(self):
        while True:
            x = random.randrange(0, self.width // self.block_size)
            # Start y range after play margin
            y = random.randrange(self.play_margin // self.block_size, self.height // self.block_size)
            if (x, y) not in self.snake:
                return (x, y)
    
    def move_snake(self):
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Check for collisions, including play margin
        if (new_head in self.snake or 
            new_head[0] < 0 or new_head[0] >= self.width // self.block_size or
            new_head[1] < self.play_margin // self.block_size or new_head[1] >= self.height // self.block_size):
            return False
        
        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            self.food = self.spawn_food()
            self.score += 1
            self.speed = max(0.005, self.speed * 0.95)  # Faster minimum speed
        else:
            self.snake.pop()
        
        return True
    
    def draw(self):
        self.oled.fill(0)
        
        # Draw score area separator line
        self.oled.hline(0, self.score_height - 1, self.width, 1)
        
        # Draw gameplay area separator line (subtle dotted line)
        for x in range(0, self.width, 4):
            self.oled.pixel(x, self.play_margin - 1, 1)
        
        # Draw score in top area
        self.oled.text(f'Score:{self.score}', 0, 4)  # Centered in score area
        
        # Draw snake
        for segment in self.snake:
            x, y = segment
            self.oled.fill_rect(x * self.block_size, y * self.block_size, 
                              self.block_size-1, self.block_size-1, 1)
        
        # Draw food
        fx, fy = self.food
        self.oled.fill_rect(fx * self.block_size, fy * self.block_size,
                          self.block_size-1, self.block_size-1, 1)
        
        self.oled.show()

def start_snake_game(oled, read_joystick, check_menu_return, read_button):
    game = SnakeGame(oled)
    last_move = time.ticks_ms()  # Use millisecond precision timing
    last_input = None
    BOOST_MULTIPLIER = 5.0  # 5x speed boost
    
    while True:
        if check_menu_return():
            return
        
        current_time = time.ticks_ms()
        direction = read_joystick()
        button = read_button()
        
        # Handle direction changes immediately
        if direction and direction != last_input:
            if direction == "DOWN" and game.direction != (0, 1):
                game.direction = (0, -1)
            elif direction == "UP" and game.direction != (0, -1):
                game.direction = (0, 1)
            elif direction == "RIGHT" and game.direction != (1, 0):
                game.direction = (-1, 0)
            elif direction == "LEFT" and game.direction != (-1, 0):
                game.direction = (1, 0)
            last_input = direction
        
        # Calculate current speed in milliseconds
        current_speed = int((game.speed / (BOOST_MULTIPLIER if button == "BTN1" and not check_menu_return() else 1.0) * 1000))
        
        # Check if it's time to move
        if time.ticks_diff(current_time, last_move) >= current_speed:
            if not game.move_snake():
                game.oled.fill(0)
                game.oled.text("Game Over!", 30, 20)
                game.oled.text(f"Score: {game.score}", 30, 35)
                game.oled.show()
                time.sleep(2)
                return
            game.draw()
            if check_menu_return():
                return
            last_move = current_time
        
        # Small delay to prevent CPU overload but keep responsive
        time.sleep(0.001)  # 1ms delay instead of 10ms
