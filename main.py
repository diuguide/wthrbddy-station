import machine
import utime
import network
import json
from conn import connect_to_wifi  # Import the connect_to_wifi function

# Define GPIO pins for button and LED
button_pin = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP)
led_pin = machine.Pin(16, machine.Pin.OUT)

click_count = 0
last_click_time = utime.ticks_ms()
ap = network.WLAN(network.AP_IF)
ap.active(False)

def load_wifi_credentials():
    """
    Load WiFi credentials from a file.
    
    :return: Tuple of (ssid, password) if credentials exist, otherwise (None, None)
    """
    try:
        with open('wifi_credentials.json', 'r') as f:
            credentials = json.load(f)
            return credentials['ssid'], credentials['password']
    except Exception as e:
        print(f"Failed to load WiFi credentials: {e}")
        return None, None

# Load WiFi credentials and attempt to connect
ssid, password = load_wifi_credentials()
if ssid and password:
    if connect_to_wifi(ssid, password):
        print(ssid)
        print(password)
        print("WiFi connected successfully. Running new_1.py...")
        import temp_1
        while True:
            pass  # Infinite loop to stop further execution

print('Listening for button....')
# Main loop to listen for button press
while True:
    
    if button_pin.value() == 0:
        # Button pressed (pull-up resistor configuration)
        led_pin.on()  # Turn on the LED
        utime.sleep(0.1)  # Wait for debounce time or perform other actions
        while button_pin.value() == 0:
            pass  # Wait for button release
        led_pin.off()  # Turn off the LED once the button is released
        
        click_count += 1
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, last_click_time) > 1000:
            # If more than 1 second has elapsed since last click, reset count
            click_count = 1
        last_click_time = current_time
        
        print("Button clicked. Count:", click_count)
        
        if click_count == 5:
            print("Button clicked 5 times! Creating Access Point...")
            import new_1
            
    utime.sleep(0.1)  # Small delay to debounce and reduce CPU usage
