import streamlit as st
import openai
import random
import time
import json
import os

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
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"Awesome, welcome {st.session_state.name}! Let’s crush some math together! 🚀"
            })
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
    
    # Save/Load Progress Buttons
    progress_keys = ['name', 'questions_answered', 'correct_answers', 'current_streak', 'current_level']
    progress_file = f"progress_{st.session_state.name}.json" if st.session_state.name else "progress.json"
    
    if st.button("💾 Save Progress"):
        progress_data = {k: st.session_state[k] for k in progress_keys}
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f)
        st.success("Progress saved!")
    
    if st.button("📂 Load Progress"):
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                loaded_progress = json.load(f)
            for k, v in loaded_progress.items():
                st.session_state[k] = v
            st.success("Progress loaded!")
            st.rerun()
        else:
            st.error("No saved progress found.")
    
    if st.button("🔄 Reset Progress"):
        for k in state_defaults:
            st.session_state[k] = state_defaults[k]
        st.rerun()

def generate_problem(level):
    """
    Generates a math problem based on the level.
    For level 1: simple addition/subtraction problems.
    For level 2: problems involving multiplication and division, 
             designed so that the answer is an integer.
    """
    if level == 1:
        a, b, c = random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)
        expr = f"{a} + ({b} - {c})" if random.choice([True, False]) else f"({a} - {b}) + {c}"
        try:
            answer = int(eval(expr))
        except Exception:
            expr, answer = "2 + (3 - 1)", 4
        return expr, answer

    elif level == 2:
        # Randomly choose one of two structures
        if random.choice([True, False]):
            # Structure: a * b / c with integer result.
            a = random.randint(2, 12)
            b = random.randint(2, 12)
            product = a * b
            # Find divisors of the product.
            divisors = [d for d in range(1, product + 1) if product % d == 0]
            c = random.choice(divisors)
            expr = f"{a} * {b} / {c}"
            answer = product // c
        else:
            # Structure: a / b * c with integer result.
            b = random.randint(2, 12)
            a = b * random.randint(1, 12)  # ensures a is a multiple of b.
            c = random.randint(1, 12)
            expr = f"{a} / {b} * {c}"
            answer = (a // b) * c

        return expr, answer

    else:
        # Default fallback problem
        expr = "2 + (3 - 1)"
        answer = 4
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

# Level-up prompt logic (trigger only once)
if st.session_state.current_streak >= 5 and not st.session_state.awaiting_level_up_response:
    st.session_state.awaiting_level_up_response = True

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

# Level-up button prompt
if st.session_state.awaiting_level_up_response:
    st.markdown(f"**Coach Bry:** Whoa {st.session_state.name}, 5 in a row! Ready to level up?")
    col1, col2 = st.columns(2)
    if col1.button("Yes, level up"):
         st.session_state.current_level += 1
         st.session_state.current_streak = 0
         st.session_state.awaiting_level_up_response = False
         st.session_state.messages.append({
             "role": "assistant",
             "content": f"Coach Bry: Awesome! Leveling up to level {st.session_state.current_level}. Let's tackle a new challenge!"
         })
         st.session_state.current_problem = None
         st.session_state.current_answer = None
         st.rerun()
    if col2.button("No, continue"):
         st.session_state.awaiting_level_up_response = False
         st.session_state.messages.append({
             "role": "assistant",
             "content": f"Coach Bry: No worries, {st.session_state.name}, let's keep pushing at level {st.session_state.current_level}!"
         })
         st.rerun()
    st.stop()

# Input form for answers or questions
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your Answer or Question:", key="chat_input")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    # Always append the user's message
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Attempt to interpret the input as an integer
        user_answer = int(user_input)
        st.session_state.questions_answered += 1

        # Check correctness
        if user_answer == st.session_state.current_answer:
            st.session_state.correct_answers += 1
            st.session_state.current_streak += 1

            # Generate a celebratory message from GPT
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You're Coach Bry, a friendly, enthusiastic math coach for kids. "
                                "When Lily gets an answer right, you celebrate her achievement with "
                                "an imaginative, creative, and supportive message."
                            )
                        },
                        {
                            "role": "user",
                            "content": "Lily just answered correctly. Give a short, fun, and enthusiastic congratulatory message."
                        }
                    ]
                )
                celebration = response.choices[0].message.content.strip()
            except Exception as e:
                celebration = f"Awesome job, {st.session_state.name}! You rocked that one! 🎉"

            st.session_state.messages.append({
                "role": "assistant",
                "content": celebration
            })

            # Clear the current problem
            st.session_state.current_problem = None
            st.session_state.current_answer = None

        else:
            # Wrong answer
            st.session_state.current_streak = 0
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Coach Bry: Almost! The answer was {st.session_state.current_answer}. Let’s walk through it together."
            })
            st.session_state.chat_mode = "waiting_for_hint"
            st.session_state.current_problem = None
            st.session_state.current_answer = None

    except ValueError:
        # Non-numeric input: use GPT for a general response
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You're Coach Bry, a kind, patient math coach for kids."},
                    *st.session_state.messages
                ]
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({
                "role": "assistant",
                "content": reply
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Coach Bry: Sorry, I ran into an error: {e}"
            })

    st.rerun()
