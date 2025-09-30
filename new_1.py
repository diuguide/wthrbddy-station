import network
import socket
import time
import json
import sys
import utime
import _thread
import machine as _machine


# Set up the Pico W as an access point (AP)
ap = network.WLAN(network.AP_IF)
ap.config(essid="wthrbddy setup", password="12345678")
ap.active(True)
print("Access point setup: SSID = wthrbddy setup")

# Wait for the access point to be ready
while not ap.active():
    time.sleep(1)

# Start the web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print(f"Listening on {addr}")


# Define the HTML form that will be served
html = """\
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head><title>WiFi Setup</title></head>
<body>
    <h2>Enter WiFi Credentials</h2>
    <form id="wifiForm">
        SSID: <input type="text" id="ssid" placeholder="Enter WiFi name"><br>
        Password: <input type="text" id="password" placeholder="Enter WiFi password"><br>
        <button type="submit">Connect</button>
    </form>
    <p id="statusMessage"></p>
    <script>
    document.getElementById('wifiForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const ssid = document.getElementById('ssid').value;
        const password = document.getElementById('password').value;

        fetch('/wifi', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ssid: ssid, password: password })
        })
        .then(response => {
            
            document.getElementById('statusMessage').textContent = "Process Complete! Redirecting...";
            
            // Redirect to a blank page with "Success" message
            setTimeout(() => {
                document.open();
                document.write("<h1>Success</h1>");
                document.close();
            }, 1000); // Delay for a better user experience
        })
        .catch(error => {
            document.getElementById('statusMessage').textContent = "Error: " + error;
        });
    });
    </script>
</body>
</html>
"""

def save_wifi_credentials(ssid, password):
    """
    Save WiFi credentials to a file.
    
    :param ssid: The WiFi network SSID
    :param password: The WiFi network password
    """
    credentials = {'ssid': ssid, 'password': password}
    with open('wifi_credentials.json', 'w') as f:
        json.dump(credentials, f)
    print("WiFi credentials saved to file.")

def connect_to_wifi(ssid, password, max_attempts=10, delay=2):
    """
    Attempts to connect to a WiFi network with the given SSID and password.
    
    :param ssid: The WiFi network SSID
    :param password: The WiFi network password
    :param max_attempts: The maximum number of connection attempts
    :param delay: The delay in seconds between connection attempts
    
    :return: True if connected, False if unable to connect after max_attempts
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print(f"Attempting to connect to WiFi network: {ssid}")

    wlan.connect(ssid, password)

    attempt = 0
    while attempt < max_attempts:
        print("attempt: ", attempt)
        status = wlan.status()
        print("status in attempt: ", status)
        
        # Check if the device is connected
        if status == 3:  # 2 is 'connected'
            print("Successfully connected to WiFi!")
            save_wifi_credentials(ssid, password)  # Save credentials on successful connection
            return True
        
        # Handle different statuses
        if status == 0:  # 0 is 'disconnected'
            print("Not connected, retrying...")
        elif status == 1:  # 1 is 'connecting'
            print("Connecting to WiFi...")
        elif status == 5:  # 5 is 'authentication failed'
            print("Authentication failed (wrong SSID or password).")
            break
        elif status == 6:  # 6 is 'no suitable AP found'
            print("No suitable access point found (wrong SSID or AP hidden).")
            break
        
        attempt += 1
        utime.sleep(delay)  # Wait before retrying

    print("Unable to connect to WiFi after multiple attempts.")
    return False

    

while True:
    conn, addr = s.accept()
    print(f"Connection from {addr}")
    request = conn.recv(1024).decode()

    if 'GET / ' in request:
        # Serve the HTML form when the user accesses the root URL
        conn.send(html)
    elif 'POST /wifi' in request:
        
        # Extract Content-Length
        content_length = 0
        for line in request.split("\r\n"):
            if line.startswith("Content-Length:"):
                content_length = int(line.split(":")[1].strip())
                
        print("content_length extraction: ", content_length)
        
        if content_length > 0:
            body = conn.recv(content_length).decode()
            print(f"Received body: {body}")
        
        # Handle WiFi credentials form submission
        #body = request.split("\r\n\r\n")[1]  # Extract the body of the request (JSON data)
        try:
            data = json.loads(body)  # Parse the JSON data
            ssid = data['ssid']
            password = data['password']
            print(f"Received WiFi credentials: SSID = {ssid}, Password = {password}")

            # Try to connect to the WiFi
            if connect_to_wifi(ssid, password):
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/json\r\n'
                response += '\r\n'
                response += json.dumps({'status': 'success', 'message': 'WiFi credentials saved!'})
                
                conn.send(response)
                
                time.sleep(10)
                print("about to reset...")
                _machine.reset()
                # import temp_1
                
            else:
                response = 'HTTP/1.1 400 Bad Request\r\n'
                response += 'Content-Type: application/json\r\n'
                response += '\r\n'
                response += json.dumps({'status': 'error', 'message': 'Failed to connect to WiFi'})
        except Exception as e:
            print(f"Error: {e}")
            response = 'HTTP/1.1 400 Bad Request\r\n'
            response += 'Content-Type: application/json\r\n'
            response += '\r\n'
            response += json.dumps({'status': 'error', 'message': 'Invalid JSON received'})

        conn.send(response)

    conn.close()