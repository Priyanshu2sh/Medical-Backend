# import os
# import django
# import socketio
# import re
# import base64
# import tempfile
# import whisper
# from gtts import gTTS
# from mistralai import Mistral
# from dotenv import load_dotenv

# # Load environment variables and setup Django
# load_dotenv()
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medical_books.settings")
# django.setup()

# # Initialize models
# whisper_model = whisper.load_model("small")
# client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
# MODEL = "mistral-large-latest"

# # Create Socket.IO server
# sio = socketio.AsyncServer(
#     cors_allowed_origins="*",
#     async_mode="asgi",
#     ping_interval=25,
#     ping_timeout=60,
#     logger=True,
#     engineio_logger=True
# )

# # ASGI app for Django + Socket.IO
# app = socketio.ASGIApp(sio)

# # Conversation history storage (per client)
# client_conversations = {}

# # System prompt
# SYSTEM_PROMPT = {
#     "role": "system",
#     "content": (
#         "Your name is 'MindCare Assistant', a compassionate mental health chatbot "
#         "developed by Prushal Technology Private Limited. "
#         "You ONLY answer questions related to mental health, emotional well-being, "
#         "coping strategies, mindfulness, therapy, and related topics. "
#         "If a question is unrelated to mental health (e.g., history, cooking, politics, sports), "
#         "politely refuse and redirect the user back to mental health topics. "
#         "If a crisis is detected, give emergency advice immediately. "
#         "By default, give short and simple answers. "
#         "If the user asks 'in detail', 'explain more', or similar, then provide a longer, "
#         "more detailed response."
#     )
# }

# def initialize_client_conversation(sid):
#     client_conversations[sid] = [SYSTEM_PROMPT]

# def detect_crisis(text):
#     crisis_keywords = [r"\bsuicid", r"\bkill myself\b", r"\bwant to die\b", r"\bhurt myself\b"]
#     return bool(re.search("|".join(crisis_keywords), text, flags=re.I))

# async def call_mistral(messages):
#     response = client.chat.complete(
#         model=MODEL,
#         messages=messages,
#         temperature=0.7,
#         max_tokens=512,
#     )
#     return response.choices[0].message.content

# async def generate_audio_chunks(text, chunk_size=100):
#     sentences = re.split(r'(?<=[.!?]) +', text)
#     current_chunk = ""
#     audio_chunks = []

#     for sentence in sentences:
#         if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
#             tts = gTTS(current_chunk.strip())
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
#                 tts.save(temp_audio.name)
#                 with open(temp_audio.name, "rb") as f:
#                     audio_bytes = f.read()
#                 audio_chunks.append(base64.b64encode(audio_bytes).decode('utf-8'))
#             current_chunk = sentence
#         else:
#             current_chunk += " " + sentence if current_chunk else sentence

#     if current_chunk.strip():
#         tts = gTTS(current_chunk.strip())
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
#             tts.save(temp_audio.name)
#             with open(temp_audio.name, "rb") as f:
#                 audio_bytes = f.read()
#             audio_chunks.append(base64.b64encode(audio_bytes).decode('utf-8'))

#     return audio_chunks

# @sio.event
# async def connect(sid, environ):
#     print(f"🔌 Client connected: {sid}")
#     initialize_client_conversation(sid)
#     await sio.emit("server_message", {"message": "Connected to MindCare Assistant"}, to=sid)

# @sio.event
# async def disconnect(sid):
#     print(f"❌ Client disconnected: {sid}")
#     if sid in client_conversations:
#         del client_conversations[sid]

# @sio.event
# async def voice_message(sid, data):
#     """Handle voice messages from clients"""
#     try:
#         base64_voice = data.get('voice')
        
#         if not base64_voice:
#             await sio.emit("error", {"message": "No voice data provided"}, to=sid)
#             return
        
#         # Decode base64 audio
#         audio_bytes = base64.b64decode(base64_voice)
        
#         # Save to temp file for Whisper
#         with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
#             temp_audio.write(audio_bytes)
#             temp_path = temp_audio.name
        
#         # Transcribe
#         result = whisper_model.transcribe(temp_path)
#         user_text = result["text"].strip()
        
#         # Add to conversation history
#         client_conversations[sid].append({"role": "user", "content": user_text})
        
#         # Generate response
#         if detect_crisis(user_text):
#             bot_reply = (
#                 "I'm really sorry you're feeling this way. Please contact local emergency services or a crisis hotline immediately. "
#                 "You are important, and help is available."
#             )
#         else:
#             bot_reply = await call_mistral(client_conversations[sid])
        
#         client_conversations[sid].append({"role": "assistant", "content": bot_reply})
        
#         # Generate audio response
#         audio_chunks = await generate_audio_chunks(bot_reply)
        
#         await sio.emit("assistant_response", {
#             'voice': audio_chunks,
#             'text': bot_reply
#         }, to=sid)
        
#     except Exception as e:
#         await sio.emit("error", {"message": str(e)}, to=sid)

# @sio.event
# async def text_message(sid, data):
#     """Handle text messages from clients"""
#     try:
#         user_text = data.get('text', '').strip()
        
#         if not user_text:
#             await sio.emit("error", {"message": "No text provided"}, to=sid)
#             return
        
#         # Add to conversation history
#         client_conversations[sid].append({"role": "user", "content": user_text})
        
#         # Generate response
#         if detect_crisis(user_text):
#             bot_reply = (
#                 "I'm really sorry you're feeling this way. Please contact local emergency services or a crisis hotline immediately. "
#                 "You are important, and help is available."
#             )
#         else:
#             bot_reply = await call_mistral(client_conversations[sid])
        
#         client_conversations[sid].append({"role": "assistant", "content": bot_reply})
        
#         # Generate audio response
#         audio_chunks = await generate_audio_chunks(bot_reply)
        
#         await sio.emit("assistant_response", {
#             'voice': audio_chunks,
#             'text': bot_reply
#         }, to=sid)
        
#     except Exception as e:
#         await sio.emit("error", {"message": str(e)}, to=sid)