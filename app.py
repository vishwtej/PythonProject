import os
import time
import streamlit as st
import requests
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
CRICKET_API_KEY = os.getenv("CRICKET_API_KEY", "b871b387-98d6-48af-ab82-1c039580a8ac")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

# ✅ Added language argument
def stream_response_from_groq(user_input, language_instruction):
    messages = [
        {"role": "system", "content": language_instruction},
        {"role": "user", "content": user_input}
    ]
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
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

# UI setup
st.set_page_config(page_title="🏆 Sports Explorer", page_icon="⚽", layout="centered")

col1, col2 = st.columns([1, 1])
with col1:
    theme = st.toggle("🌗 Dark Mode", key="theme_toggle")
with col2:
    if st.button("🔁 Reset Chat"):
        st.session_state.chat_history = []
        st.rerun()

# 🎨 Theme Styling (unchanged)...

# Title
st.markdown("## 🏆 Sports Explorer Chatbot")
st.caption("Talk sports like a pro — cricket, football, basketball, fitness, and more!")

# ✅ Language selection dropdown
language = st.selectbox("🌐 Choose Language", ["English", "Hindi", "Marathi", "Gujarati", "Spanish", "French"])
language_map = {
    "English": "Reply in English.",
    "Hindi": "Reply in Hindi.",
    "Marathi": "Reply in Marathi.",
    "Gujarati": "Reply in Gujarati.",
    "Spanish": "Reply in Spanish.",
    "French": "Reply in French."
}
language_instruction = language_map.get(language, "Reply in English.")

# Session states
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# Chat Input
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("💬 Your message:", placeholder="Ask about any sport...")
    submitted = st.form_submit_button("📤 Send")

# Chat Handling
if submitted and user_input:
    st.session_state.chat_history.append(("You", user_input))

    if is_sports_related(user_input):
        if "live" in user_input.lower() and "cricket" in user_input.lower():
            with st.spinner("📡 Fetching live cricket scores..."):
                cricket_response = get_live_cricket_score()
                feedback_id = str(len(st.session_state.chat_history))
                st.session_state.chat_history.append(("Bot", cricket_response, feedback_id))
        else:
            with st.spinner("🤖 Typing..."):
                placeholder = st.empty()
                full_response = ""
                for chunk in stream_response_from_groq(user_input, language_instruction):
                    full_response += chunk
                    placeholder.markdown(f"""
                    <div class="chat-row">
                        <div class="chat-bubble bot-bubble">
                            🤖 Bot:<br>{full_response}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                feedback_id = str(len(st.session_state.chat_history))
                st.session_state.chat_history.append(("Bot", full_response, feedback_id))
    else:
        msg = "🚫 Please ask about sports-related topics only."
        feedback_id = str(len(st.session_state.chat_history))
        st.session_state.chat_history.append(("Bot", msg, feedback_id))

# Display Chat
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
