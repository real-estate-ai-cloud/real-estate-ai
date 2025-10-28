from flask import Flask, request, jsonify
from openai import OpenAI
import requests
import os

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DEEPGRAM_KEY = os.environ.get("DEEPGRAM_KEY")
FROM_NUMBER = os.environ.get("SINCH_NUMBER", "+1416XXXXXXX")

client = OpenAI(api_key=OPENAI_API_KEY)

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
    data = request.get_json(silent=True) or {}
    call_id = data.get("callId")
    greeting = "Hi, this is Abhinav with HomeLife Miracle Realty. Got a quick moment to chat?"
    audio_url = text_to_speech(greeting)
    return jsonify({
        "actions": [
            {"action": "play", "url": audio_url},
            {"action": "input", "dtmf": True, "speech": True, "timeout": 5}
        ],
        "next": "https://your-app.onrender.com/webhook"
    })

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    user_text = data.get("input", {}).get("speech", "")

    if not user_text:
        return jsonify({"actions": [{"action": "hangup"}]})

    messages = [
        {"role": "system", "content": MIKE_FERRY_PROMPT},
        {"role": "user", "content": user_text},
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )
        ai_reply = completion.choices[0].message.content
    except Exception as e:
        print("OpenAI error:", e)
        ai_reply = "Sorry, I had trouble responding. Could you repeat that?"

    audio_url = text_to_speech(ai_reply)
    return jsonify({
        "actions": [
            {"action": "play", "url": audio_url},
            {"action": "input", "dtmf": True, "speech": True, "timeout": 5}
        ],
        "next": "https://your-app.onrender.com/webhook"
    })

def text_to_speech(text):
    url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
    headers = {
        "Authorization": f"Token {DEEPGRAM_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print("Deepgram TTS error:", response.text)
            return "https://static.deepgram.com/examples/hello.mp3"
        filename = "/tmp/output.wav"
        with open(filename, "wb") as f:
            f.write(response.content)
        return "https://static.deepgram.com/examples/hello.mp3"
    except Exception as e:
        print("TTS error:", e)
        return "https://static.deepgram.com/examples/hello.mp3"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
