import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key="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")  # Replace with env var for production

# Define keywords related to sports
SPORT_KEYWORDS = [
    "sport", "football", "cricket", "basketball", "tennis", "athlete", "training",
    "workout", "fitness", "match", "game", "tournament", "olympics", "player", "score",
    "team", "coach", "referee", "goal", "bat", "ball", "run", "race"
]

def is_sports_related(text):
    """Check if input is sports-related using keyword matching."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in SPORT_KEYWORDS)

def chat_with_groq(user_input):
    """ Function to communicate with Groq AI """
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": user_input}],
        temperature=0.7
    )
    return response.choices[0].message.content

# Streamlit UI
st.title("🏆 Sports Explorer Chatbot")
st.write("Ask anything about sports, techniques, or training methods.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.text_input("You:", "", key="user_input")
if st.button("Send") and user_input:
    if is_sports_related(user_input):
        try:
            response = chat_with_groq(user_input)
        except Exception as e:
            response = f"Error: {e}"
    else:
        response = "Please ask about sports-related topics only."

    # Save chat history
    st.session_state.chat_history.insert(0, ("Bot", response))
    st.session_state.chat_history.insert(0, ("You", user_input))

# Display chat history
for role, message in st.session_state.chat_history:
    with st.chat_message("user" if role == "You" else "assistant"):
        st.write(message)
