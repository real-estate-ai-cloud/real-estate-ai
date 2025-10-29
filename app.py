from flask import Flask, request, jsonify
import openai
import requests
import os

app = Flask(__name__)

# === ENVIRONMENT VARIABLES ===
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DEEPGRAM_KEY = os.environ.get("DEEPGRAM_KEY")
FROM_NUMBER = os.environ.get("FROM_NUMBER")  # Your Sinch number

if not OPENAI_API_KEY or not DEEPGRAM_KEY or not FROM_NUMBER:
    raise ValueError("Please set OPENAI_API_KEY, DEEPGRAM_KEY, and FROM_NUMBER in environment variables.")

openai.api_key = OPENAI_API_KEY

# MIKE FERRY PROMPT (full version)
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

# --- Root route ---
@app.route("/")
def index():
    return "Real Estate AI is running!"

# --- /voice endpoint ---
@app.route("/voice", methods=["POST"])
def voice():
    data = request.json
    call_id = data.get("callId")

    greeting = "Hi, this is Abhinav with HomeLife Miracle Realty. Got a quick moment to chat?"
    audio_url = text_to_speech(greeting)

    return jsonify({
        "actions": [
            {"action": "play", "url": audio_url},
            {"action": "input", "dtmf": True, "speech": True, "timeout": 5}
        ],
        "next": "/webhook"
    })

# --- /webhook endpoint ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    user_text = data.get("input", {}).get("speech", "")

    if not user_text:
        return jsonify({"actions": [{"action": "hangup"}]})

    messages = [
        {"role": "system", "content": MIKE_FERRY_PROMPT},
        {"role": "user", "content": user_text}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )
    ai_reply = response.choices[0].message.content

    audio_url = text_to_speech(ai_reply)

    return jsonify({
        "actions": [
            {"action": "play", "url": audio_url},
            {"action": "input", "dtmf": True, "speech": True, "timeout": 5}
        ],
        "next": "/webhook"
    })

# --- Deepgram TTS ---
def text_to_speech(text):
    url = "https://api.deepgram.com/v1/speak"
    headers = {
        "Authorization": f"Token {DEEPGRAM_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    response = requests.post(url, json=payload, headers=headers, params={"model": "nova-2"})
    return response.json().get("url", "")

# --- Entry point for gunicorn ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
