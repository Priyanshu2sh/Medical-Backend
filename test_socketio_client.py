# import socketio

# sio = socketio.Client()

# @sio.event
# def connect():
#     print("✅ Connected to server")

# @sio.event
# def disconnect():
#     print("❌ Disconnected from server")

# @sio.on('bot_response')
# def handle_bot_response(data):
#     print("🤖 Bot says:", data)

# print("Connecting...")
# # If your namespace is "/example", put it like this:
# sio.connect('http://192.168.1.57:8080', namespaces=['/example'])

# # Emit a test event
# sio.emit('send_voice', {'voice_base64': '...'}, namespace='/example')

# sio.wait()
