import base64
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class Consumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_json({
            "type": "connection",
            "message": "WebSocket connected successfully."
        })

    async def disconnect(self, code):
        await self.send_json({
            "type": "disconnection",
            "message": f"WebSocket disconnected. Code: {code}"
        })

    async def receive_json(self, content, **kwargs):
        voice_data = content.get("voice", "")

        try:
            decoded_bytes = base64.b64decode(voice_data)
            decoded_text = decoded_bytes.decode("utf-8", errors="ignore")
        except Exception:
            decoded_text = "[Error decoding base64]"

        await self.send_json({
            "voice": voice_data,
            "text": decoded_text
        })
