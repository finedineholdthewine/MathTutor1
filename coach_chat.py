import streamlit as st
import openai
import random

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
if 'current_problem' not in st.session_state:
    st.session_state.current_problem = None
if 'current_answer' not in st.session_state:
    st.session_state.current_answer = None

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
    """.format(
        st.session_state.questions_answered,
        st.session_state.correct_answers,
        accuracy,
        st.session_state.current_streak
    ))
    if st.button("🔄 Reset Progress"):
        st.session_state.questions_answered = 0
        st.session_state.correct_answers = 0
        st.session_state.current_streak = 0
        st.session_state.messages = []
        st.session_state.current_problem = None
        st.session_state.current_answer = None
        st.rerun()

# Generate new math problem
if st.session_state.current_problem is None:
    a, b = random.randint(1, 10), random.randint(1, 10)
    st.session_state.current_problem = f"What is {a} + {b}?"
    st.session_state.current_answer = a + b
    st.session_state.messages.append({"role": "assistant", "content": f"Alright, here’s your next challenge: {st.session_state.current_problem} ✏️"})

# Display all messages first
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**{msg['content']}**")

# Then show input form LAST to keep it on screen
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
            feedback = "Boom! You nailed it! ✅ Ready for the next one?"
        else:
            st.session_state.current_streak = 0
            feedback = f"Almost! The correct answer was {st.session_state.current_answer}. Let's try another one!"
    except ValueError:
        feedback = "Hmm, that doesn’t look like a number. Try entering a number next time!"

    st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: {feedback}"})
    st.session_state.current_problem = None
    st.session_state.current_answer = None
    st.rerun()
