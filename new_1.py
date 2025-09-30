import network
import socket
import time
import json
import utime
import machine
from conn import connect_to_wifi, save_wifi_credentials
from config import AP_SSID, AP_PASSWORD


# Set up the Pico W as an access point (AP)
ap = network.WLAN(network.AP_IF)
ap.config(essid=AP_SSID, password=AP_PASSWORD)
ap.active(True)
print("Access point setup: SSID =", AP_SSID)

# Wait for the access point to be ready
while not ap.active():
    time.sleep(1)

# Start the web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print(f"Listening on {addr}")


# Function to generate HTML response - saves memory by not storing large string
def get_html_response():
    return ("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
            "<html><head><title>WiFi Setup</title></head><body>"
            "<h2>WiFi Setup</h2><form id='f'>"
            "SSID: <input type='text' id='s'><br>"
            "Password: <input type='text' id='p'><br>"
            "<button onclick='c()'>Connect</button></form>"
            "<p id='m'></p><script>"
            "function c(){var s=document.getElementById('s').value;"
            "var p=document.getElementById('p').value;"
            "fetch('/wifi',{method:'POST',headers:{'Content-Type':'application/json'},"
            "body:JSON.stringify({ssid:s,password:p})}).then(()=>{"
            "document.getElementById('m').textContent='Success! Device restarting...';});"
            "}</script></body></html>")



while True:
    conn, addr = s.accept()
    print(f"Connection from {addr}")
    request = conn.recv(1024).decode()

    if 'GET / ' in request:
        # Serve the HTML form when the user accesses the root URL
        conn.send(get_html_response())
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
                save_wifi_credentials(ssid, password)  # Save credentials on successful connection
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/json\r\n'
                response += '\r\n'
                response += json.dumps({'status': 'success', 'message': 'WiFi credentials saved!'})
                
                conn.send(response)
                
                time.sleep(2)  # Reduced delay for better UX
                print("about to reset...")
                machine.reset()
                
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