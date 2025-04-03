import streamlit as st
import openai
import time
import os
import json
from utils import generate_problem, save_progress, load_progress

openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-openai-api-key")

st.set_page_config(page_title="Coach Chatbot", page_icon="🤖")

# --- Custom CSS ---
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
    'mode_selected': False,
    'chat_mode': None,
    'challenge_start_time': None,
    'challenge_score': 0,
    'challenge_active': False,
    'current_streak': 0,
    'snake_unlocked': False,
    'snake_displayed': False,
    'snake_celebrated': False,  # to avoid double GPT messages
    'current_problem': None,
    'current_answer': None,
    'current_level': 1,
    'awaiting_level_up_response': False,
    'chat_mode': 'ready',  # Modes: ready, waiting_for_hint, showing_hint
    'last_problem': ''
}
for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- UI Functions ---

def display_mode_selector():
    st.markdown(f"### Hey there, {st.session_state.name}! What would you like to do today?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧠 Practice Mode"):
            st.session_state.mode_selected = True
            st.session_state.chat_mode = "normal"
            st.rerun()
    with col2:
        if st.button("⏱️ 60-Second Challenge"):
            st.session_state.mode_selected = True
            st.session_state.chat_mode = "timed_challenge"
            st.session_state.challenge_start_time = time.time()
            st.session_state.challenge_score = 0
            st.session_state.challenge_active = True
            st.rerun()

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
        
        col1, col2, col3 = st.columns(3)
        if col1.button("💾 Save Progress"):
            save_progress(st.session_state, progress_file)
            st.success("Progress saved!")
        if col2.button("📂 Load Progress"):
            loaded = load_progress(progress_file)
            if loaded:
                for key, val in loaded.items():
                    st.session_state[key] = val
                st.success("Progress loaded!")
                st.rerun()
            else:
                st.error("No saved progress found.")
        if col3.button("🔄 Reset Progress"):
            for key, value in state_defaults.items():
                st.session_state[key] = value
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

def handle_problem_generation():
    if (st.session_state.current_problem is None and 
        not st.session_state.awaiting_level_up_response and 
        st.session_state.chat_mode == "ready"):
        expr, answer = generate_problem(st.session_state.current_level)
        st.session_state.current_problem = expr
        st.session_state.current_answer = answer
        st.session_state.last_problem = expr
        
        # Display a tip based on level
        if st.session_state.current_level == 1:
            tip = "Remember—parentheses first!"
        elif st.session_state.current_level == 2:
            tip = "Multiply and divide left to right!"
        elif st.session_state.current_level == 3:
            tip = "Remember: Solve inside parentheses first, then multiply, then subtract!"
        else:
            tip = ""
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Coach Bry: Level {st.session_state.current_level} challenge: `{expr}` ✏️ {tip}"
        })

def handle_hint_logic():
    if st.session_state.chat_mode == "waiting_for_hint":
        st.session_state.chat_mode = "showing_hint"
        hint_prompt = f"Give a short hint to a middle schooler for solving this math problem step-by-step: {st.session_state.last_problem}. Keep it positive and clear."
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": hint_prompt}]
            )
            hint = response.choices[0].message.content
        except Exception as e:
            hint = "Sorry, I ran into an error generating a hint. Let's think about the steps carefully!"
        st.session_state.messages.append({"role": "assistant", "content": f"Coach Bry: {hint}"})
        st.rerun()
    elif st.session_state.chat_mode == "showing_hint":
        st.session_state.chat_mode = "ready"
        st.rerun()

def handle_level_up_prompt():
    if st.session_state.current_streak >= 5 and not st.session_state.awaiting_level_up_response:
        st.session_state.awaiting_level_up_response = True
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

def display_input_form():
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Your Answer or Question:", key="chat_input")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            user_answer = int(user_input)
            st.session_state.questions_answered += 1

            if user_answer == st.session_state.current_answer:
                st.session_state.correct_answers += 1
                st.session_state.current_streak += 1

                if st.session_state.current_streak == 10 and not st.session_state.snake_unlocked:
                    st.session_state.snake_unlocked = True
                    try:
                        gpt_reward = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": (
                                    f"You're Coach Bry, a fun, hype math coach for kids. "
                                    f"When {st.session_state.name} gets 10 correct in a row, you reward them with a surprise game. "
                                    f"Celebrate with excitement!"
                                )},
                                {"role": "user", "content": f"{st.session_state.name} just got 10 math problems right in a row. Announce their reward: a Snake Game!"}
                            ]
                        )
                        celebration = gpt_reward.choices[0].message.content.strip()
                    except Exception:
                        celebration = f"🔥 Whoa {st.session_state.name}, 10 in a row?! You just unlocked the Snake Game! 🐍🎮"

                    st.session_state.snake_celebrated = True
                    st.session_state.messages.append({"role": "assistant", "content": celebration})
                else:
                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        f"You're Coach Bry, a friendly, enthusiastic math coach for kids. "
                                        f"When {st.session_state.name} gets an answer right, you celebrate with a short, creative message."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": f"{st.session_state.name} just answered correctly. Congratulate them!"
                                }
                            ]
                        )
                        celebration = response.choices[0].message.content.strip()
                    except Exception:
                        celebration = f"Awesome job, {st.session_state.name}! You rocked that one! 🎉"

                    st.session_state.messages.append({"role": "assistant", "content": celebration})

                st.session_state.current_problem = None
                st.session_state.current_answer = None

            else:
                st.session_state.current_streak = 0
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Coach Bry: Almost! The answer was {st.session_state.current_answer}. Let’s walk through it together."
                })
                st.session_state.chat_mode = "waiting_for_hint"
                st.session_state.current_problem = None
                st.session_state.current_answer = None

        except ValueError:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You're Coach Bry, a kind, patient math coach for kids."},
                        *st.session_state.messages
                    ]
                )
                reply = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Coach Bry: Sorry, I ran into an error: {e}"
                })

        st.rerun()  # ✅ Fixes double-submit + refreshes form

# 🐍 Show Snake Game (non-blocking version)
def display_snake_game():
    st.markdown("## 🐍 Snake Game Reward!")
    st.markdown("You've earned it! Enjoy your break 🎉")

    import streamlit.components.v1 as components
    components.iframe("https://playsnake.org/", height=500, scrolling=True)

    st.session_state.snake_displayed = True

# 🧠 DEBUG - See what's happening
st.write("✅ DEBUG → Snake Unlocked:", st.session_state.get("snake_unlocked"))
st.write("✅ DEBUG → Snake Displayed:", st.session_state.get("snake_displayed"))

# --- Main Execution Flow ---

if not st.session_state.name_submitted:
    display_name_prompt()

if not st.session_state.mode_selected:
    display_mode_selector()
    st.stop()

if (
    st.session_state.snake_unlocked 
    and not st.session_state.snake_displayed
):
    display_snake_game()

display_progress()
handle_hint_logic()
handle_level_up_prompt()
handle_problem_generation()
display_messages()
display_input_form()
