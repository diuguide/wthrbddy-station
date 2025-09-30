# Configuration constants for the weather station
# Shared across all modules to reduce memory usage

# Hardware pin assignments
BUTTON_PIN = 17
LED_PIN = 16
DHT_PIN = 15

# Network settings
AP_SSID = "wthrbddy setup"
AP_PASSWORD = "12345678"
BASE_URL = "https://intense-idea-281222.ue.r.appspot.com/inbound/"
STATION_ID = 1

# Timing constants
CLICK_TIMEOUT = 1000  # milliseconds
LONG_PRESS_TIME = 10000  # milliseconds
POLL_INTERVAL = 200  # milliseconds
POLL_CHECKS = 5  # number of polling cycles

# File names
CREDENTIALS_FILE = 'wifi_credentials.json'