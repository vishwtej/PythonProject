import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key="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")  # Ensure your API key is stored correctly in .env
def chat_with_groq(user_input):
    """ Function to communicate with Groq AI """
    response = client.chat.completions.create(
        model="llama3-8b-8192",  # Replace with the correct Groq model name
        messages=[{"role": "user", "content": user_input}],
        temperature=0.7
    )
    return response.choices[0].message.content
# Streamlit UI
st.title("Sports Explorer Chatbot")
st.write("Ask anything about sports, techniques, or training methods.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.text_input("You:", "", key="user_input")
if st.button("Send") and user_input:
    try:
        response = chat_with_groq(user_input)
        
        # Save chat history
        st.session_state.chat_history.insert(0, ("Bot", response))
        st.session_state.chat_history.insert(0, ("You", user_input))
    except Exception as e:
        response = f"Error: {e}"
        st.session_state.chat_history.insert(0, ("Bot", response))
# Display chat history
for role, message in st.session_state.chat_history:
    with st.chat_message("user" if role == "You" else "assistant"):
        st.write(message)