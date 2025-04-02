import streamlit as st
import openai
import random
import time

openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-openai-api-key")

st.set_page_config(page_title="Coach Chatbot", page_icon="🤖")

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
    border: 2px solid #ff9900; /* Orange border for the current message */
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

# Initialize state
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
    'chat_mode': 'ready',  # Modes: ready, waiting_for_hint, showing_hint, ready_for_new_problem
    'last_problem': ''
}
for k, v in state_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state.name_submitted:
    st.session_state.messages = []
    st.markdown("**Coach Bry:** Hey there, superstar! What’s your name so I can cheer you on properly? 🌟")
    with st.form(key="name_form"):
        st.session_state.name = st.text_input("Enter your name")
        name_submit = st.form_submit_button("Let's Go!")
        if name_submit and st.session_state.name.strip() != "":
            st.session_state.name_submitted = True
            st.session_state.current_level = 1
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Awesome, welcome {st.session_state.name}! Let’s crush some math together! 🚀"})
            st.session_state.chat_mode = "ready"
            st.rerun()
    st.stop()

# Progress display
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
    if st.button("🔄 Reset Progress"):
        for k in state_defaults:
            st.session_state[k] = state_defaults[k]
        st.rerun()

def generate_problem(level):
    if level == 1:
        a, b, c = random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)
        expr = f"{a} + ({b} - {c})" if random.choice([True, False]) else f"({a} - {b}) + {c}"
    elif level == 2:
        a, b, c = random.randint(2, 12), random.randint(1, 10), random.randint(1, 10)
        expr = f"{a} * {b} / {c}" if random.choice([True, False]) else f"{a} / {b} * {c}"
    else:
        expr = "2 + (3 - 1)"
    try:
        answer = int(eval(expr))
    except:
        expr, answer = "2 + (3 - 1)", 4
    return expr, answer

# Stage logic for staggered feedback → hint → problem
if st.session_state.chat_mode == "waiting_for_hint":
    st.session_state.chat_mode = "showing_hint"
    hint_prompt = f"Give a short hint to a middle schooler for solving this math problem step-by-step: {st.session_state.last_problem}. Keep it positive and clear."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": hint_prompt}]
    )
    hint = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: {hint}"})
    st.rerun()

elif st.session_state.chat_mode == "showing_hint":
    st.session_state.chat_mode = "ready"
    st.rerun()

# Level-up prompt logic
if st.session_state.current_streak >= 5 and not st.session_state.awaiting_level_up_response:
    st.session_state.awaiting_level_up_response = True
    st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Whoa {st.session_state.name}, 5 in a row?! Want to level up? Type 'yes' or 'no'."})

# Generate new question if ready
if st.session_state.current_problem is None and not st.session_state.awaiting_level_up_response and st.session_state.chat_mode == "ready":
    expr, answer = generate_problem(st.session_state.current_level)
    st.session_state.current_problem = expr
    st.session_state.current_answer = answer
    st.session_state.last_problem = expr
    tip = "Remember—parentheses first!" if st.session_state.current_level == 1 else "Multiply and divide left to right!"
    st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Level {st.session_state.current_level} challenge: `{expr}` ✏️ {tip}"})

# Display last 4 chat messages
messages_to_display = st.session_state.messages[-4:]
for i, msg in enumerate(messages_to_display):
    role_class = "user-bubble" if msg["role"] == "user" else "bry-bubble"
    # If this is the last message, add the 'current-message' class for extra styling
    if i == len(messages_to_display) - 1:
        role_class += " current-message"
    st.markdown(
        f'<div class="chat-bubble {role_class} clearfix">{msg["content"]}</div>',
        unsafe_allow_html=True
    )

# Input
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your Answer or Question:", key="chat_input")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.awaiting_level_up_response:
        if user_input.lower() == "yes":
            st.session_state.current_level += 1
            st.session_state.current_streak = 0
            st.session_state.awaiting_level_up_response = False
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Let’s gooo! Welcome to Level {st.session_state.current_level}, {st.session_state.name}!"})
        elif user_input.lower() == "no":
            st.session_state.current_streak = 0
            st.session_state.awaiting_level_up_response = False
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: No problem! Let’s keep sharpening our skills here."})
        st.rerun()

    try:
        user_answer = int(user_input)
        st.session_state.questions_answered += 1
        if user_answer == st.session_state.current_answer:
            st.session_state.correct_answers += 1
            st.session_state.current_streak += 1
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Nailed it, {st.session_state.name}! ✅"})
            st.session_state.current_problem = None
            st.session_state.current_answer = None
        else:
            st.session_state.current_streak = 0
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Almost! The answer was {st.session_state.current_answer}. Let’s walk through it together."})
            st.session_state.chat_mode = "waiting_for_hint"
            st.session_state.current_problem = None
            st.session_state.current_answer = None
    except ValueError:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You're Coach Bry, a kind, patient math coach for kids."}, *st.session_state.messages]
        )
        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: {reply}"})

    st.rerun()
