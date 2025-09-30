import dht
import machine
import time
import urequests
import network
import os
from config import DHT_PIN, LED_PIN, BUTTON_PIN, BASE_URL, STATION_ID, LONG_PRESS_TIME, POLL_INTERVAL, POLL_CHECKS, CREDENTIALS_FILE

# Function to read data from DHT22 sensor
def read_dht22(pin):
    d = dht.DHT22(machine.Pin(pin))  # Create DHT22 object
    d.measure()  # Perform measurement
    temperature_celsius = d.temperature()  # Read temperature in Celsius
    humidity = d.humidity()  # Read humidity
    # Convert temperature to Fahrenheit
    temperature_fahrenheit = (temperature_celsius * 9/5) + 32
    return temperature_fahrenheit, humidity

# Main function
def main():
    wlan = network.WLAN(network.STA_IF)
    print("wlan status in temp.py:", wlan.status())

    # LED pin (same as used in main.py)
    led = machine.Pin(LED_PIN, machine.Pin.OUT)

    # persistent hold start (in milliseconds) across iterations
    hold_start_ms = None

    while True:
        try:
            # Read data from DHT22 sensor
            temperature, humidity = read_dht22(DHT_PIN)
            print("Temperature:", temperature, "F")
            print("Humidity:", humidity, "%")

            # Construct URL with temperature and humidity as data points
            url = "{}{:.1f}-{:.1f}-{}".format(BASE_URL, temperature, humidity, STATION_ID)
            print("URL:", url)

            # Send GET request
            response = urequests.get(url)
            print("Response:", response.text)
            response.close()

            # Check for long-press on the same button used in main.py.
            # If held for >= 10 seconds, delete wifi_credentials.json and restart.
            button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

            # Poll in small intervals while still performing sensor reads
            for _ in range(POLL_CHECKS):
                pressed = (button.value() == 0)  # active low
                if pressed:
                    # Turn LED on while held
                    led.on()

                    now = time.ticks_ms()
                    if hold_start_ms is None:
                        hold_start_ms = now
                    else:
                        held_ms = time.ticks_diff(now, hold_start_ms)
                        if held_ms >= LONG_PRESS_TIME:
                            print("Long press detected. Removing credentials and restarting...")
                            try:
                                if CREDENTIALS_FILE in os.listdir('.'):
                                    os.remove(CREDENTIALS_FILE)
                                    print('Credentials deleted')
                                else:
                                    print('Credentials file not found')
                            except Exception as e:
                                print('Failed to delete credentials:', e)
                            # Ensure LED is off before reset
                            led.off()
                            time.sleep(0.2)
                            machine.reset()
                else:
                    # Button not pressed: turn LED off and reset hold timer
                    led.off()
                    hold_start_ms = None

                # small delay in milliseconds
                time.sleep(POLL_INTERVAL/1000)

            time.sleep(0.5)
        except Exception as e:
            print("Error:", e)
            time.sleep(10)  # Retry after 10 seconds if there's an error

# Run the main function
main()

