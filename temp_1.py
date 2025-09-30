import dht
import machine
import time
import urequests
import network
import os
import machine as _machine

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
    # Define DHT22 pin
    dht_pin = 15  # Replace with the GPIO pin connected to the DHT22 sensor

    sample_ip = ""
    port = "8080"
    station_id=001

    # Base URL for the GET request
    base_url = "https://intense-idea-281222.ue.r.appspot.com/inbound/"
    wlan = network.WLAN(network.STA_IF)
    #wlan.active(True)
    
    print("wlan status in temp.py:", wlan.status())

    # LED pin (same as used in main.py)
    led = machine.Pin(16, machine.Pin.OUT)

    # persistent hold start (in milliseconds) across iterations
    hold_start_ms = None

    while True:
        try:
            # Read data from DHT22 sensor
            temperature, humidity = read_dht22(dht_pin)
            print("Temperature:", temperature, "F")
            print("Humidity:", humidity, "%")

            # Construct URL with temperature and humidity as data points
            url = base_url + str(temperature) + "-" + str(humidity) + "-" + str(station_id) 
            print("URL:", url)

            # Send GET request
            response = urequests.get(url)
            print("Response:", response.text)
            response.close()

            # Check for long-press on the same button used in main.py (GPIO17).
            # If held for >= 10 seconds, delete wifi_credentials.json and restart.
            button = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP)

            # Poll in small intervals while still performing sensor reads
            poll_interval = 200  # milliseconds
            checks = 5  # total ~1 second of polling between sensor cycles
            for _ in range(checks):
                pressed = (button.value() == 0)  # active low
                if pressed:
                    # Turn LED on while held
                    try:
                        led.on()
                    except Exception:
                        pass

                    now = time.ticks_ms()
                    if hold_start_ms is None:
                        hold_start_ms = now
                    else:
                        held_ms = time.ticks_diff(now, hold_start_ms)
                        if held_ms >= 10000:  # 10 seconds
                            print("Long press detected (>=10s). Removing wifi_credentials.json and restarting...")
                            try:
                                if 'wifi_credentials.json' in os.listdir('.'):
                                    os.remove('wifi_credentials.json')
                                    print('wifi_credentials.json deleted')
                                else:
                                    print('wifi_credentials.json not found')
                            except Exception as e:
                                print('Failed to delete wifi_credentials.json:', e)
                            # Ensure LED is off before reset
                            try:
                                led.off()
                            except Exception:
                                pass
                            time.sleep(0.2)
                            _machine.reset()
                else:
                    # Button not pressed: turn LED off and reset hold timer
                    try:
                        led.off()
                    except Exception:
                        pass
                    hold_start_ms = None

                # small delay in milliseconds
                time.sleep(poll_interval/1000)

            time.sleep(0.5)
        except Exception as e:
            print("Error:", e)
            time.sleep(10)  # Retry after 10 seconds if there's an error

# Run the main function
main()

