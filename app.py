import streamlit as st
import random

# Set page title and icon
st.set_page_config(page_title="Math Tutor", page_icon="🧠")

# Centered title with emoji
st.markdown("<h1 style='text-align: center;'>Welcome to Lily's Adaptive Math Tutor! 🧮</h1>", unsafe_allow_html=True)

# Instructions
st.markdown("""
<div style='text-align: center;'>
Answer 5 questions in a row correctly to level up!
</div>
---
""", unsafe_allow_html=True)

def generate_problem(level):
    if level == 1:
        a, b = random.randint(1, 10), random.randint(1, 10)
        return f"{a} + {b}", a + b
    elif level == 2:
        a, b = random.randint(10, 50), random.randint(1, 20)
        return f"{a} - {b}", a - b
    elif level == 3:
        a, b = random.randint(1, 10), random.randint(1, 10)
        return f"{a} × {b}", a * b
    elif level == 4:
        b = random.randint(1, 10)
        a = b * random.randint(1, 10)
        return f"{a} ÷ {b}", a // b

# Track session state
if 'level' not in st.session_state:
    st.session_state.level = 1
    st.session_state.correct = 0
    st.session_state.problem, st.session_state.answer = generate_problem(1)

# Display current problem
st.subheader(f"Level {st.session_state.level}")
st.markdown(f"**Solve:** {st.session_state.problem}")
user_answer = st.text_input("Your Answer:")

# Evaluate input
if user_answer:
    try:
        if int(user_answer) == st.session_state.answer:
            st.success("Correct!")
            st.session_state.correct += 1
            if st.session_state.correct >= 5:
                st.session_state.level += 1
                st.balloons()
                st.info(f"Great job! You've advanced to level {st.session_state.level}!")
                st.session_state.correct = 0
            # Generate new problem after correct answer
            st.session_state.problem, st.session_state.answer = generate_problem(st.session_state.level)
        else:
            st.error(f"Oops! That's not correct. Try again!")
    except ValueError:
        st.warning("Please enter a valid number.")
