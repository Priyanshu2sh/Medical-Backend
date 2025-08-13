import os
import re
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from mistralai import Mistral

# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise RuntimeError("Please set MISTRAL_API_KEY in your environment or .env file")

# Initialize Mistral client
client = Mistral(api_key=MISTRAL_API_KEY)
MODEL = "mistral-medium-latest"

# System prompt
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Your name is 'MindCare Assistant', a compassionate mental health chatbot "
        "developed by Prushal Technology Private Limited. "
        "You ONLY answer questions related to mental health, emotional well-being, "
        "coping strategies, mindfulness, therapy, and related topics. "
        "If a question is unrelated to mental health (e.g., history, cooking, politics, sports), "
        "politely refuse and redirect the user back to mental health topics. "
        "If a crisis is detected, give emergency advice immediately. "
        "By default, give short and simple answers. "
        "If the user asks 'in detail', 'explain more', or similar, then provide a longer, "
        "more detailed response."
    )
}

# Conversation history storage (in-memory for this example)
conversation_history = [SYSTEM_PROMPT]

# Crisis detection
def detect_crisis(text):
    crisis_keywords = [r"\bsuicid", r"\bkill myself\b", r"\bwant to die\b", r"\bhurt myself\b"]
    return bool(re.search("|".join(crisis_keywords), text, flags=re.I))

# Call Mistral API
def call_mistral(messages):
    response = client.chat.complete(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content

@csrf_exempt
def mindcare_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        user_input = data.get('message', '').strip()
        if not user_input:
            return JsonResponse({'error': 'Empty message'}, status=400)

        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_input})

        if detect_crisis(user_input):
            bot_reply = (
                "I'm really sorry you're feeling this way. Please contact local emergency services or a crisis hotline immediately. "
                "You are important, and help is available."
            )
        else:
            bot_reply = call_mistral(conversation_history)

        # Add assistant response to conversation history
        conversation_history.append({"role": "assistant", "content": bot_reply})

        return JsonResponse({
            'response': bot_reply,
            # 'status': 'success'
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)
