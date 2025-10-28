# 🧠 AI Realtor Voice Agent

A Flask-based AI calling assistant that integrates **Sinch**, **OpenAI**, and **Deepgram** to converse with leads using natural voice.

## 🚀 Features
- Handles inbound Sinch voice webhooks.
- Uses **OpenAI GPT-4o-mini** to generate natural responses.
- Converts text replies to speech using **Deepgram TTS**.
- Fully deployable to **Render** with environment variables.

## 🛠️ Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/YOURUSERNAME/ai-agent.git
cd ai-agent
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Add Your .env File
```
OPENAI_API_KEY=sk-your-openai-key
DEEPGRAM_KEY=dg-your-deepgram-key
SINCH_NUMBER=+1416XXXXXXX
```

### 5. Run Locally
```bash
python app.py
```

### 6. Deploy to Render
- Connect your GitHub repo on Render.
- Set environment variables in the dashboard.
- Use `python app.py` as Start Command.

## 👤 Author
**Abhinav** — Realtor & Developer  
*HomeLife Miracle Realty*
