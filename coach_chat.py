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
    st.session_state.current_level = 2
if 'awaiting_level_up_response' not in st.session_state:
    st.session_state.awaiting_level_up_response = False

# Ask for name at the start
if not st.session_state.name_submitted:
    st.session_state.messages = []
    st.markdown("**Coach Bry:** Hey there, superstar! What’s your name so I can cheer you on properly? 🌟")
    with st.form(key="name_form"):
        st.session_state.name = st.text_input("Enter your name")
        name_submit = st.form_submit_button("Let's Go!")
        if name_submit and st.session_state.name.strip() != "":
            st.session_state.name_submitted = True
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Awesome, welcome {st.session_state.name}! Let’s crush some math together! 🚀"})
            st.rerun()
    st.stop()

# Progress display
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
        st.session_state.awaiting_level_up_response = False
        st.rerun()

# Level 2 problem generator
def generate_level2():
    a = random.randint(2, 12)
    b = random.randint(1, 10)
    c = random.randint(1, 10)
    expr = f"{a} * {b} / {c}" if random.choice([True, False]) else f"{a} / {b} * {c}"
    try:
        answer = int(eval(expr))
    except:
        expr, answer = "6 * 2 / 3", 4
    return expr, answer

# Check for level-up prompt
if st.session_state.current_streak >= 5 and not st.session_state.awaiting_level_up_response:
    st.session_state.awaiting_level_up_response = True
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"Coach Bry: Whoa {st.session_state.name}, 5 in a row?! That’s amazing! Want to try something a little tougher? Type 'yes' to level up or 'no' to keep practicing here."
    })

# Only generate a new problem if not awaiting level-up response
if st.session_state.current_problem is None and not st.session_state.awaiting_level_up_response:
    expr, answer = generate_level2()
    st.session_state.current_problem = expr
    st.session_state.current_answer = answer
    st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Alright {st.session_state.name}, here’s your Level {st.session_state.current_level} challenge: `{expr}` ✏️ Multiply and divide left to right!"})

# Show only the last 3 messages
for msg in st.session_state.messages[-3:]:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**{msg['content']}**")

# Input form at the bottom
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your Answer or Question:", key="chat_input")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.awaiting_level_up_response:
        if user_input.lower() == "yes":
            st.session_state.current_level += 1
            st.session_state.awaiting_level_up_response = False
            st.session_state.current_streak = 0
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Let’s gooo! Welcome to Level {st.session_state.current_level}, {st.session_state.name}! Time to step it up!"})
        elif user_input.lower() == "no":
            st.session_state.awaiting_level_up_response = False
            st.session_state.current_streak = 0
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: No problem! We’ll stay here a little longer and master this level together."})
        st.rerun()

    try:
        user_answer = int(user_input)
        st.session_state.questions_answered += 1
        if user_answer == st.session_state.current_answer:
            st.session_state.correct_answers += 1
            st.session_state.current_streak += 1
            feedback = f"Nice job, {st.session_state.name}! ✅ Multiplication and division handled like a pro!"
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: {feedback}"})
            st.session_state.current_problem = None
            st.session_state.current_answer = None
        else:
            st.session_state.current_streak = 0
            wrong_feedback = f"Almost! The correct answer was {st.session_state.current_answer}. Let’s walk through it."
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: {wrong_feedback}"})
            hint_prompt = f"Give a short hint to a middle schooler for solving this math problem step-by-step: {st.session_state.current_problem}. Keep it positive and clear."
            hint_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": hint_prompt}]
            )
            hint = hint_response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: {hint}"})
            st.session_state.current_problem = None
            st.session_state.current_answer = None

    except ValueError:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're Coach Bry, a kind, patient math coach for kids. Speak clearly, use examples, and encourage questions. Always be supportive and friendly."},
                *st.session_state.messages
            ]
        )
        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: {reply}"})

    st.rerun()
