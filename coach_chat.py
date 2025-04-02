import streamlit as st
import openai
import random
import time
import os
import json

from utils import generate_problem, save_progress, load_progress  # Import our helper functions

openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-openai-api-key")

st.set_page_config(page_title="Coach Chatbot", page_icon="🤖")

# --- Define CSS & Page Title ---
st.markdown("""
<style>
.chat-bubble {
    padding: 0.7rem 1rem;
    border-radius: 1rem;
    margin-bottom: 0.5rem;
    max-width: 85%;
    display: inline-block;
}
.user-bubble {
    background-color: #e0e0e0;
    color: black;
    text-align: right;
    float: right;
}
.bry-bubble {
    background-color: #d0f0fd;
    color: black;
    text-align: left;
    float: left;
}
.current-message {
    border: 2px solid #ff9900;
    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
}
.clearfix::after {
    content: "";
    display: block;
    clear: both;
}
</style>
""", unsafe_allow_html=True)

st.title("🏀 Coach Bry - Math Motivation Chat")

# --- Session State Defaults ---
state_defaults = {
    'name': '',
    'name_submitted': False,
    'messages': [],
    'questions_answered': 0,
    'correct_answers': 0,
    'current_streak': 0,
    'current_problem': None,
    'current_answer': None,
    'current_level': 1,
    'awaiting_level_up_response': False,
    'chat_mode': 'ready',
    'last_problem': ''
}
for k, v in state_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- UI Functions ---
def display_name_prompt():
    st.markdown("**Coach Bry:** Hey there, superstar! What’s your name so I can cheer you on properly? 🌟")
    with st.form(key="name_form"):
        st.session_state.name = st.text_input("Enter your name")
        name_submit = st.form_submit_button("Let's Go!")
        if name_submit and st.session_state.name.strip() != "":
            st.session_state.name_submitted = True
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"Awesome, welcome {st.session_state.name}! Let’s crush some math together! 🚀"
            })
            st.session_state.chat_mode = "ready"
            st.rerun()
    st.stop()

def display_progress():
    with st.expander("📊 Progress (click to expand/collapse)", expanded=False):
        acc = 0
        if st.session_state.questions_answered > 0:
            acc = round((st.session_state.correct_answers / st.session_state.questions_answered) * 100)
        st.markdown(f"""
        - Questions Answered: {st.session_state.questions_answered}
        - Correct: {st.session_state.correct_answers}
        - Accuracy: {acc}%
        - Current Streak: {st.session_state.current_streak} ✅
        - Current Level: {st.session_state.current_level}
        """)
        progress_file = f"progress_{st.session_state.name}.json" if st.session_state.name else "progress.json"
        if st.button("💾 Save Progress"):
            save_progress(st.session_state, progress_file)
            st.success("Progress saved!")
        if st.button("📂 Load Progress"):
            loaded = load_progress(progress_file)
            if loaded:
                for k, v in loaded.items():
                    st.session_state[k] = v
                st.success("Progress loaded!")
                st.rerun()
            else:
                st.error("No saved progress found.")
        if st.button("🔄 Reset Progress"):
            for k in state_defaults:
                st.session_state[k] = state_defaults[k]
            st.rerun()

def display_messages():
    messages_to_display = st.session_state.messages[-4:]
    for i, msg in enumerate(messages_to_display):
        role_class = "user-bubble" if msg["role"] == "user" else "bry-bubble"
        if i == len(messages_to_display) - 1:
            role_class += " current-message"
        st.markdown(
            f'<div class="chat-bubble {role_class} clearfix">{msg["content"]}</div>',
            unsafe_allow_html=True
        )

# --- Main App Flow ---
if not st.session_state.name_submitted:
    display_name_prompt()

display_progress()

# ... (remaining logic for generating problems, handling input, etc.) ...
