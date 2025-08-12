# import websocket
# import json
# import base64

# # Connect to WebSocket
# ws = websocket.create_connection("ws://192.168.1.57:8080/ws/example/")

# # Example plain text we pretend is "audio"
# original_text = "Hello from client"
# dummy_audio = base64.b64encode(original_text.encode()).decode()

# # Send
# ws.send(json.dumps({"voice": dummy_audio}))

# # Receive
# result = ws.recv()
# print("Received:", result)

# ws.close()
