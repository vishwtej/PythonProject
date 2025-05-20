import os
import streamlit as st
import requests
from dotenv import load_dotenv
from groq import Groq
# from googletrans import Translator  # Removed old googletrans
from deep_translator import GoogleTranslator  # Added deep_translator

# Load environment variables
load_dotenv()
CRICKET_API_KEY = os.getenv("CRICKET_API_KEY", "b871b387-98d6-48af-ab82-1c039580a8ac")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize translator from deep_translator
translator = GoogleTranslator(source='auto', target='en')

# Supported languages for translation dropdown (code: name)
LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "hi": "Hindi",
    "de": "German",
    "zh-cn": "Chinese (Simplified)",
    "ar": "Arabic",
    "ru": "Russian",
    # Add more languages if needed
}

SPORT_KEYWORDS = [
    "sport", "football", "cricket", "basketball", "tennis", "athlete", "training",
    "workout", "fitness", "match", "game", "tournament", "olympics", "player", "score",
    "team", "coach", "referee", "goal", "bat", "ball", "run", "race"
]

def is_sports_related(text):
    return any(keyword in text.lower() for keyword in SPORT_KEYWORDS)

def get_live_cricket_score():
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={CRICKET_API_KEY}&offset=0"
    try:
        res = requests.get(url)
        data = res.json()

        if not data.get("data"):
            return "❌ No live matches found at the moment."

        matches = data["data"][:5]
        scores = []
        for match in matches:
            team1 = match.get("teamInfo", [{}])[0].get("name", "Team A")
            team2 = match.get("teamInfo", [{}])[1].get("name", "Team B")
            score = match.get("score", [])
            status = match.get("status", "Status not available")

            score_text = f"🏏 {team1} vs {team2}\n📣 Status: {status}"
            if score:
                for s in score:
                    score_text += f"\n   - {s.get('inning')}: {s.get('r')}/{s.get('w')} in {s.get('o')} overs"
            scores.append(score_text)

        return "\n\n".join(scores)

    except Exception as e:
        return f"⚠️ Error fetching live scores: {str(e)}"

def stream_response_from_groq(user_input):
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": user_input}],
        temperature=0.7,
        stream=True
    )

    full_reply = ""
    for chunk in response:
        content = chunk.choices[0].delta.content if chunk.choices[0].delta else ""
        if content:
            full_reply += content
            yield content
    return full_reply

# Configure page
st.set_page_config(page_title="🏆 Sports Explorer", page_icon="⚽", layout="centered")

selected_lang = st.selectbox("🌐 Select Language / भाषा चुनें", options=list(LANGUAGES.values()), index=0)
selected_lang_code = [code for code, name in LANGUAGES.items() if name == selected_lang][0]

col1, col2 = st.columns([1, 1])
with col1:
    theme = st.toggle("🌗 Dark Mode", key="theme_toggle")
with col2:
    if st.button("🔁 Reset Chat"):
        st.session_state.chat_history = []
        st.rerun()

if theme:
    st.markdown("""
        <style>
        body { background: #121212; color: #ffffff; }
        .chat-bubble { background: #333; color: #eee; }
        .user-bubble { background-color: #4caf50; color: #fff; }
        .bot-bubble { background-color: #2196f3; color: #fff; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        body { background: linear-gradient(135deg, #f0f9ff, #c2f0c2); }
        .chat-bubble {
            padding: 12px;
            margin: 8px 0;
            border-radius: 18px;
            max-width: 80%;
            font-size: 16px;
            animation: fadeIn 0.5s ease-in;
        }
        .user-bubble {
            background-color: #dcf8c6;
            color: #1a3c34;
            border: 2px solid #4caf50;
            align-self: flex-end;
        }
        .bot-bubble {
            background-color: #fff3cd;
            color: #3b2f2f;
            border: 2px solid #ffcc80;
            align-self: flex-start;
        }
        .chat-row {
            display: flex;
            flex-direction: column;
            width: 100%;
        }
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(5px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        </style>
    """, unsafe_allow_html=True)

st.markdown("## 🏆 Sports Explorer Chatbot")
st.caption("Talk sports like a pro — cricket, football, basketball, fitness, and more!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "feedback" not in st.session_state:
    st.session_state.feedback = {}

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("💬 Your message:", placeholder="Ask about any sport...")
    submitted = st.form_submit_button("📤 Send")

if submitted and user_input:
    # Translate user input to English before sending to model if needed
    if selected_lang_code != "en":
        # Reset translator source and target dynamically for user input
        translator.source = selected_lang_code
        translator.target = "en"
        translated_input = translator.translate(user_input)
    else:
        translated_input = user_input

    st.session_state.chat_history.append(("You", user_input))

    if is_sports_related(translated_input):
        if "live" in translated_input.lower() and "cricket" in translated_input.lower():
            with st.spinner("📡 Fetching live cricket scores..."):
                cricket_response = get_live_cricket_score()
                if selected_lang_code != "en":
                    translator.source = "en"
                    translator.target = selected_lang_code
                    cricket_response = translator.translate(cricket_response)
                feedback_id = str(len(st.session_state.chat_history))
                st.session_state.chat_history.append(("Bot", cricket_response, feedback_id))
        else:
            with st.spinner("🤖 Typing..."):
                placeholder = st.empty()
                full_response = ""
                for chunk in stream_response_from_groq(translated_input):
                    full_response += chunk
                    display_text = full_response
                    if selected_lang_code != "en":
                        translator.source = "en"
                        translator.target = selected_lang_code
                        display_text = translator.translate(full_response)
                    placeholder.markdown(f"""
                    <div class="chat-row">
                        <div class="chat-bubble bot-bubble">
                            🤖 Bot:<br>{display_text}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                feedback_id = str(len(st.session_state.chat_history))
                st.session_state.chat_history.append(("Bot", display_text, feedback_id))
    else:
        msg = "🚫 Please ask about sports-related topics only."
        if selected_lang_code != "en":
            translator.source = "en"
            translator.target = selected_lang_code
            msg = translator.translate(msg)
        feedback_id = str(len(st.session_state.chat_history))
        st.session_state.chat_history.append(("Bot", msg, feedback_id))

for message in st.session_state.chat_history:
    if message[0] == "You":
        st.markdown(f"""
        <div class="chat-row">
            <div class="chat-bubble user-bubble">
                🧑 You:<br>{message[1]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        role, msg, fid = message
        st.markdown(f"""
        <div class="chat-row">
            <div class="chat-bubble bot-bubble">
                🤖 Bot:<br>{msg}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("👍", key=f"up_{fid}"):
                st.session_state.feedback[fid] = "up"
                st.success("You liked this response!")
        with col2:
            if st.button("👎", key=f"down_{fid}"):
                st.session_state.feedback[fid] = "down"
                st.warning("You disliked this response.")

st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)
