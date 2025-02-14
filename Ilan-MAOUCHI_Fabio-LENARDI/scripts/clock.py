from machine import I2C, Pin, ADC
from ssd1306 import SSD1306_I2C
from urtc import DS1307, datetime_tuple
import time

# Initialize I2C for OLED and RTC
i2c = I2C(0, sda=Pin(0), scl=Pin(1))

pin = Pin(16, Pin.OUT)
pin.value(0)  # Set GPIO16 low to reset OLED
time.sleep(0.1)  # Short delay to ensure reset
pin.value(1)  # Set GPIO16 high while OLED is running

oled_width = 128
oled_height = 64

oled = SSD1306_I2C(oled_width, oled_height, i2c)

i2c = I2C(1, scl=Pin(7), sda=Pin(6))
rtc = DS1307(i2c)

# Setup joystick and button
joystick_x = ADC(Pin(27))
joystick_y = ADC(Pin(26))
button = Pin(14, Pin.IN, Pin.PULL_UP)  # Changed to standard push button

# Constants
THRESHOLD = 3000  # Threshold for joystick movement detection
DEBOUNCE_TIME = 200  # Debounce time in milliseconds

class ClockSetter:
    def __init__(self):
        self.current_field = 0
        self.fields = ['Year', 'Month', 'Day', 'Weekday', 'Hour', 'Minute', 'Second']
        self.last_move_time = 0
        
    def read_joystick(self):
        x = joystick_x.read_u16()
        y = joystick_y.read_u16()
        return x, y
    
    def debounce(self):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_move_time) > DEBOUNCE_TIME:
            self.last_move_time = current_time
            return True
        return False
    
    def adjust_value(self, dt_list, increment):
        # Limits for each field (year, month, day, weekday, hour, minute, second)
        limits = [(2000, 2099), (1, 12), (1, 31), (0, 6), (0, 23), (0, 59), (0, 59)]
        current_value = dt_list[self.current_field]
        min_val, max_val = limits[self.current_field]
        
        new_value = current_value + increment
        if new_value > max_val:
            new_value = min_val
        elif new_value < min_val:
            new_value = max_val
            
        dt_list[self.current_field] = new_value
        return dt_list
    
    def display_datetime(self, dt, setting_mode=False):
        oled.fill(0)
        
        # Display date
        date_str = f"{dt.day:02d}/{dt.month:02d}/{dt.year}"
        oled.text(date_str, 0, 0)
        
        # Display time
        time_str = f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
        oled.text(time_str, 0, 20)
        
        # Display weekday
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        oled.text(weekdays[dt.weekday], 0, 30)
        
        # In setting mode, show which field is being edited
        if setting_mode:
            oled.text("Setting:", 0, 40)
            oled.text(self.fields[self.current_field], 10, 50)
            
        oled.show()

def wait_button_release():
    while not button.value():
        time.sleep_ms(50)

def main():
    clock_setter = ClockSetter()
    setting_mode = False
    last_button_state = True
    
    while True:
        current_button_state = button.value()
        
        if not setting_mode:
            # Normal mode - display current time
            current_time = rtc.datetime()
            clock_setter.display_datetime(current_time)
            
            # Check for button press to enter setting mode
            if not current_button_state and last_button_state:
                setting_mode = True
                # Convert current time to list for editing
                dt_list = [
                    current_time.year,
                    current_time.month,
                    current_time.day,
                    current_time.weekday,
                    current_time.hour,
                    current_time.minute,
                    current_time.second
                ]
                wait_button_release()
                time.sleep_ms(200)  # Additional debounce
                
        else:
            # Setting mode
            x, y = clock_setter.read_joystick()
            
            if clock_setter.debounce():
                if x < THRESHOLD:  # Left
                    clock_setter.current_field = (clock_setter.current_field - 1) % len(clock_setter.fields)
                elif x > 65535 - THRESHOLD:  # Right
                    clock_setter.current_field = (clock_setter.current_field + 1) % len(clock_setter.fields)
                elif y < THRESHOLD:  # Down
                    dt_list = clock_setter.adjust_value(dt_list, 1)
                elif y > 65535 - THRESHOLD:  # Up
                    dt_list = clock_setter.adjust_value(dt_list, -1)
            
            # Create datetime tuple for display
            current_dt = datetime_tuple(
                year=dt_list[0],
                month=dt_list[1],
                day=dt_list[2],
                weekday=dt_list[3],
                hour=dt_list[4],
                minute=dt_list[5],
                second=dt_list[6],
                millisecond=0
            )
            
            # Display current setting state
            clock_setter.display_datetime(current_dt, True)
            
            # Exit setting mode and save if button is pressed
            if not current_button_state and last_button_state:
                rtc.datetime(current_dt)
                setting_mode = False
                wait_button_release()
                time.sleep_ms(200)  # Additional debounce
        
        last_button_state = current_button_state
        time.sleep_ms(100)

if __name__ == '__main__':
    main()