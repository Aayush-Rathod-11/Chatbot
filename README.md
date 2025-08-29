# Conversational AI Chatbot — Demo

## Summary

This demo shows a conversational chatbot with:

- Local fallback (KB, fuzzy matching)
- Optional OpenAI Chat mode (uses system prompt + history)
- Session memory, clear, download chat

## Run (Windows)

1. python -m venv venv
2. venv\Scripts\activate Note : If error ocurre the before activate thats commnd : "Set-ExecutionPolicy RemoteSigned -Scope Process" run and then activate venv.
3. pip install -r requirements.txt
4. set FLASK_APP=app.py
5. python -m flask run

Open http://127.0.0.1:5000

## Git (push to your GitHub)

1. git init
2. git add .
3. git commit -m "Add Initial Files"
4. On GitHub: create repo e.g. `yourname/chatbot-demo`
5. git remote add origin https://github.com/<your-username>/<your-repo>.git
6. git branch -M main
7. git push -u origin main

## To use OpenAI mode

- Either set environment var `OPENAI_API_KEY` before running, or paste key in UI settings.
- Warning: sending API key from browser has security implications; better to set server env var in production.

## Next steps (to impress your mentor)

- Add embeddings + vector DB (FAISS or Pinecone)
- Add user authentication + persistent DB (SQLite)
- Add file upload + retrieval (PDF -> embeddings)
- Deploy to Heroku/Render/Vercel (backend on Render/Heroku)
