import streamlit as st
import openai
import random

# Set your OpenAI API key here or use secrets
openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-openai-api-key")

st.set_page_config(page_title="Coach Chatbot", page_icon="🤖")

st.title("🏀 Coach Bry - Math Motivation Chat")

# Initialize session state
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'name_submitted' not in st.session_state:
    st.session_state.name_submitted = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'questions_answered' not in st.session_state:
    st.session_state.questions_answered = 0
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0
if 'current_streak' not in st.session_state:
    st.session_state.current_streak = 0
if 'current_problem' not in st.session_state:
    st.session_state.current_problem = None
if 'current_answer' not in st.session_state:
    st.session_state.current_answer = None
if 'current_level' not in st.session_state:
    st.session_state.current_level = 1

# Ask for name at the start
if not st.session_state.name_submitted:
    st.session_state.messages = []  # Clear chat when name starts fresh
    st.markdown("**Coach Bry:** Hey there, superstar! What’s your name so I can cheer you on properly? 🌟")
    with st.form(key="name_form"):
        st.session_state.name = st.text_input("Enter your name")
        name_submit = st.form_submit_button("Let's Go!")
        if name_submit and st.session_state.name.strip() != "":
            st.session_state.name_submitted = True
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Awesome, welcome {st.session_state.name}! Let’s crush some math together! 🚀"})
            st.rerun()
    st.stop()

# Display progress at the top
if st.session_state.questions_answered > 0:
    accuracy = round((st.session_state.correct_answers / st.session_state.questions_answered) * 100)
else:
    accuracy = 0

with st.expander("📊 Progress (click to expand/collapse)", expanded=True):
    st.markdown("""
    - Questions Answered: {0}
    - Correct: {1}
    - Accuracy: {2}%
    - Current Streak: {3} ✅
    - Current Level: {4}
    """.format(
        st.session_state.questions_answered,
        st.session_state.correct_answers,
        accuracy,
        st.session_state.current_streak,
        st.session_state.current_level
    ))
    if st.button("🔄 Reset Progress"):
        st.session_state.questions_answered = 0
        st.session_state.correct_answers = 0
        st.session_state.current_streak = 0
        st.session_state.messages = []
        st.session_state.current_problem = None
        st.session_state.current_answer = None
        st.session_state.name = ""
        st.session_state.name_submitted = False
        st.session_state.current_level = 1
        st.rerun()

# LEVEL 1: Parentheses + Add/Subtract
if st.session_state.current_problem is None:
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    c = random.randint(1, 10)
    expr = f"{a} + ({b} - {c})" if random.choice([True, False]) else f"({a} - {b}) + {c}"
    try:
        answer = eval(expr)
    except:
        expr, answer = "2 + (3 - 1)", 4
    st.session_state.current_problem = expr
    st.session_state.current_answer = answer
    st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Alright {st.session_state.name}, here’s your Level 1 challenge: `{st.session_state.current_problem}` ✏️ Remember—parentheses first!"})

# Show only the last 3 messages
for msg in st.session_state.messages[-3:]:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**{msg['content']}**")

# Input form at the bottom
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your Answer:", key="chat_input")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.questions_answered += 1
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        if int(user_input) == st.session_state.current_answer:
            st.session_state.correct_answers += 1
            st.session_state.current_streak += 1
            feedback = f"Boom! You nailed it, {st.session_state.name}! ✅ Remember: Parentheses come first!"
        else:
            st.session_state.current_streak = 0
            feedback = f"Almost! The correct answer was {st.session_state.current_answer}. Try breaking it down step-by-step: parentheses first!"
    except ValueError:
        feedback = "Hmm, that doesn’t look like a number. Try entering a number next time!"

    st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: {feedback}"})
    st.session_state.current_problem = None
    st.session_state.current_answer = None
    st.rerun()