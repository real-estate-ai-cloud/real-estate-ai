from flask import Flask, request, jsonify
import openai
import requests
import os

app = Flask(__name__)

# === API KEYS ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "PASTE_OPENAI_KEY_HERE")
DEEPGRAM_KEY = os.getenv("DEEPGRAM_KEY", "PASTE_DEEPGRAM_KEY_HERE")
FROM_NUMBER = os.getenv("FROM_NUMBER", "+1416XXXXXXX")

openai.api_key = OPENAI_API_KEY

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

# === HOMEPAGE ROUTE ===
@app.route("/")
def home():
    return "✅ Real Estate AI Agent is live and ready!"

# === TEST ROUTE ===
@app.route("/test")
def test():
    """Simple OpenAI test without Sinch or Deepgram"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly assistant."},
                {"role": "user", "content": "Say hello as Abhinav, the realtor."}
            ],
            temperature=0.7
        )
        return jsonify({"message": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)})

# === SINCH VOICE ROUTE ===
@app.route("/voice", methods=['POST'])
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

# === WEBHOOK ROUTE ===
@app.route("/webhook", methods=['POST'])
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

# === TEXT TO SPEECH ===
def text_to_speech(text):
    url = "https://api.deepgram.com/v1/speak"
    headers = {
        "Authorization": f"Token {DEEPGRAM_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    response = requests.post(url, json=payload, headers=headers, params={"model": "aura-asteria-en"})
    return response.json().get("url", "")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

