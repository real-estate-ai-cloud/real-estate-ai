from flask import Flask, request, jsonify
import openai
import requests
import os

app = Flask(__name__)

# === KEYS FROM ENV VARIABLES (set these in Render Dashboard) ===
openai.api_key = os.getenv("OPENAI_API_KEY")
DEEPGRAM_KEY = os.getenv("DEEPGRAM_KEY")
FROM_NUMBER = os.getenv("FROM_NUMBER", "+1416XXXXXXX")  # Optional fallback

# === MIKE FERRY PROMPT ===
MIKE_FERRY_PROMPT = """
You are Abhinav, expert realtor with HomeLife Miracle Realty.
Goal: Book 15-min consult.
1. Greeting: 'Hi, this is Abhinav with HomeLife Miracle Realty. Is this [Name]? Got a quick moment?'
2. Probe: 'Have you thought about buying or selling in the next 3-6 months?'
3. If yes: 'Where would you go next?' → 'How soon?'
4. If no: 'What would make you consider moving?'
5. Objections:
   - 'Not interested': 'I hear you. Happy where you are, or something holding you back?'
   - 'Market high': 'Worried about price? I find undervalued homes.'
   - 'Renting': 'Thought about buying to build equity?'
6. Close: 'Let’s do a quick 15-min call. Tuesday 10 AM or 2 PM? Call 555-1234.'
"""

@app.route("/voice", methods=["POST"])
def voice():
    # Sinch sends JSON: {"callId": "...", "from": "...", "to": "..."}
    data = request.json or {}
    call_id = data.get("callId", "")

    greeting = "Hi, this is Abhinav with HomeLife Miracle Realty. Got a quick moment to chat?"
    audio_url = text_to_speech(greeting)

    return jsonify({
        "actions": [
            {"action": "play", "url": audio_url},
            {"action": "input", "dtmf": True, "speech": True, "timeout": 5}
        ],
        "next": "/webhook"
    })

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    user_text = data.get("input", {}).get("speech", "")

    if not user_text:
        return jsonify({"actions": [{"action": "hangup"}]})

    # AI ChatCompletion (using OpenAI 0.28.0)
    messages = [
        {"role": "system", "content": MIKE_FERRY_PROMPT},
        {"role": "user", "content": user_text}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    ai_reply = response["choices"][0]["message"]["content"]
    audio_url = text_to_speech(ai_reply)

    return jsonify({
        "actions": [
            {"action": "play", "url": audio_url},
            {"action": "input", "dtmf": True, "speech": True, "timeout": 5}
        ],
        "next": "/webhook"
    })

def text_to_speech(text):
    """Send text to Deepgram TTS and return audio URL."""
    url = "https://api.deepgram.com/v1/speak"
    headers = {
        "Authorization": f"Token {DEEPGRAM_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    response = requests.post(url, json=payload, headers=headers, params={"model": "nova-2"})

    if response.ok and "url" in response.json():
        return response.json()["url"]
    return ""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

