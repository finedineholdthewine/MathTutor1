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
    align-self: flex-end;
    text-align: right;
    float: right;
}
.bry-bubble {
    background-color: #d0f0fd;
    color: black;
    align-self: flex-start;
    text-align: left;
    float: left;
}
.clearfix::after {
    content: "";
    display: block;
    clear: both;
}
</style>
""", unsafe_allow_html=True)

st.title("🏀 Coach Bry - Math Motivation Chat")

# Initialize session state
defaults = {
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
    'pending_hint': False,
    'just_sent_hint': False
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if not st.session_state.name_submitted:
    st.session_state.messages = []
    st.markdown("**Coach Bry:** Hey there, superstar! What’s your name so I can cheer you on properly? 🌟")
    with st.form(key="name_form"):
        st.session_state.name = st.text_input("Enter your name")
        name_submit = st.form_submit_button("Let's Go!")
        if name_submit and st.session_state.name.strip() != "":
            st.session_state.name_submitted = True
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Awesome, welcome {st.session_state.name}! Let’s crush some math together! 🚀"})
            st.session_state.just_sent_hint = True
            st.rerun()
    st.stop()

# Progress
if st.session_state.questions_answered > 0:
    accuracy = round((st.session_state.correct_answers / st.session_state.questions_answered) * 100)
else:
    accuracy = 0

with st.expander("📊 Progress (click to expand/collapse)", expanded=False):
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
        for key in list(st.session_state.keys()):
            del st.session_state[key]
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

# Handle staged hint delivery
if st.session_state.pending_hint:
    st.session_state.pending_hint = False
    problem = st.session_state.last_problem if 'last_problem' in st.session_state else ""
    hint_prompt = f"Give a short hint to a middle schooler for solving this math problem step-by-step: {problem}. Keep it positive and clear."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": hint_prompt}]
    )
    hint = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: {hint}"})
    st.session_state.just_sent_hint = True
    st.rerun()

# Wait a round after sending a hint before generating a new question
if st.session_state.just_sent_hint:
    st.session_state.just_sent_hint = False
    st.rerun()

# Level up prompt
if st.session_state.current_streak >= 5 and not st.session_state.awaiting_level_up_response:
    st.session_state.awaiting_level_up_response = True
    st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Whoa {st.session_state.name}, 5 in a row?! Want to level up? Type 'yes' or 'no'."})

# Generate a new problem
if st.session_state.current_problem is None and not st.session_state.awaiting_level_up_response:
    expr, answer = generate_problem(st.session_state.current_level)
    st.session_state.current_problem = expr
    st.session_state.current_answer = answer
    st.session_state.last_problem = expr
    tip = "Remember—parentheses first!" if st.session_state.current_level == 1 else "Multiply and divide left to right!"
    st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Level {st.session_state.current_level} challenge: `{expr}` ✏️ {tip}"})

# Show chat messages
for msg in st.session_state.messages[-4:]:
    bubble_class = "user-bubble" if msg["role"] == "user" else "bry-bubble"
    st.markdown(f'<div class="chat-bubble {bubble_class} clearfix">{msg["content"]}</div>', unsafe_allow_html=True)

# Input form
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
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Let’s gooo! Welcome to Level {st.session_state.current_level}, {st.session_state.name}!"})
        elif user_input.lower() == "no":
            st.session_state.awaiting_level_up_response = False
            st.session_state.current_streak = 0
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: No problem! Let’s keep sharpening our skills here."})
        st.rerun()

    try:
        user_answer = int(user_input)
        st.session_state.questions_answered += 1
        if user_answer == st.session_state.current_answer:
            st.session_state.correct_answers += 1
            st.session_state.current_streak += 1
            st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: Awesome, {st.session_state.name}! ✅ You rocked that one."})
            st.session_state.current_problem = None
            st.session_state.current_answer = None
        else:
            st.session_state.current_streak = 0
            feedback = f"Coach Bry: Almost! The answer was {st.session_state.current_answer}. Let’s go over it."
            st.session_state.messages.append({"role": "assistant", "content": feedback})
            st.session_state.pending_hint = True
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

    st.rerun()
