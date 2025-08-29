from flask import Flask, render_template, request, jsonify, session
import os, json, difflib

# Optional OpenAI import
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')  # change for prod

# Load KB
KB_PATH = os.path.join(os.path.dirname(__file__), 'kb.json')
with open(KB_PATH, 'r', encoding='utf-8') as f:
    KB = json.load(f)

def local_bot_response(user_message: str):
    """
    Simple local fallback using fuzzy matching against KB keys.
    """
    keys = list(KB.keys())
    # Use close matches to find a topic
    matches = difflib.get_close_matches(user_message.lower(), [k.lower() for k in keys], n=1, cutoff=0.4)
    if matches:
        # Find original key (case-insensitive match)
        for k in keys:
            if k.lower() == matches[0]:
                return KB[k]
    # If no close match, give a friendly fallback
    suggestions = ", ".join(keys[:5])
    return ("Sorry — I didn't quite get that. Try one of these topics: " + suggestions
            + "\nOr ask 'how to run' or 'features'.")

def call_openai_chat(messages, api_key=None, temperature=0.7):
    if not OPENAI_AVAILABLE:
        raise RuntimeError("OpenAI SDK not installed. Install 'openai' in your environment to use model mode.")
    # Use provided api_key or environment variable
    if api_key:
        openai.api_key = api_key
    # Build call to ChatCompletion (gpt-3.5-turbo)
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=float(temperature),
        max_tokens=400
    )
    return resp['choices'][0]['message']['content'].strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json or {}
    user_message = (data.get('message') or "").strip()
    mode = data.get('mode', 'local')  # 'local' or 'openai'
    system_prompt = data.get('system_prompt', "You are a helpful assistant.")
    temperature = data.get('temperature', 0.7)
    api_key = data.get('api_key') or os.environ.get('OPENAI_API_KEY')

    if 'history' not in session:
        session['history'] = []

    history = session['history']  # list of {'role':..., 'content':...}

    if mode == 'openai' and api_key:
        # Build messages with system prompt and previous history
        messages = [{'role': 'system', 'content': system_prompt}]
        # convert stored history to chat format (they should already be compatible)
        messages.extend(history)
        messages.append({'role': 'user', 'content': user_message})
        try:
            reply = call_openai_chat(messages, api_key=api_key, temperature=temperature)
        except Exception as e:
            reply = f"OpenAI error: {str(e)}"
    else:
        # local fallback
        reply = local_bot_response(user_message)

    # Save conversation in session (keep last 40 messages)
    history.append({'role': 'user', 'content': user_message})
    history.append({'role': 'assistant', 'content': reply})
    session['history'] = history[-40:]

    return jsonify({'reply': reply, 'history': session['history']})

@app.route('/api/clear', methods=['POST'])
def api_clear():
    session.pop('history', None)
    return jsonify({'status': 'cleared'})

if __name__ == "__main__":
    app.run(debug=True)
