import streamlit as st
import openai
import os

# Set your OpenAI API key here or use secrets
openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-openai-api-key")

st.set_page_config(page_title="Coach Chatbot", page_icon="🤖")

st.title("🏀 Coach Bry - Math Motivation Chat")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'questions_answered' not in st.session_state:
    st.session_state.questions_answered = 0
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0
if 'current_streak' not in st.session_state:
    st.session_state.current_streak = 0

# Reset button
if st.button("🔄 Reset Progress"):
    st.session_state.questions_answered = 0
    st.session_state.correct_answers = 0
    st.session_state.current_streak = 0
    st.session_state.messages = []
    st.experimental_rerun()

# Progress Tracker
if st.session_state.questions_answered > 0:
    accuracy = round((st.session_state.correct_answers / st.session_state.questions_answered) * 100)
else:
    accuracy = 0

st.markdown("""
### 📊 Progress
- Questions Answered: {0}
- Correct: {1}
- Accuracy: {2}%
- Current Streak: {3} ✅
---
""".format(
    st.session_state.questions_answered,
    st.session_state.correct_answers,
    accuracy,
    st.session_state.current_streak
))

# Input area
user_input = st.text_input("You:", key="input")

if user_input:
    st.session_state.questions_answered += 1
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Simulate check for correct answer
    # In a real math app, you'd validate user_input against expected answer
    if any(char.isdigit() for char in user_input):
        st.session_state.correct_answers += 1
        st.session_state.current_streak += 1
    else:
        st.session_state.current_streak = 0

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're Coach Bry, a cool and encouraging math coach who gives short, friendly replies with emojis. Keep things positive and motivating."},
            *st.session_state.messages
        ]
    )

    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Coach Bry:** {msg['content']}")
