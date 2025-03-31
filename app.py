import streamlit as st
import random

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

if 'level' not in st.session_state:
    st.session_state.level = 1
    st.session_state.correct = 0

st.title("Adaptive Math Tutor")

problem, answer = generate_problem(st.session_state.level)
user_answer = st.text_input(f"Solve: {problem}")

if user_answer:
    if user_answer.isdigit() and int(user_answer) == answer:
        st.success("Correct!")
        st.session_state.correct += 1
    else:
        st.error(f"Oops! The correct answer was {answer}.")
        st.session_state.correct = 0

    if st.session_state.correct >= 5:
        st.session_state.level += 1
        st.session_state.correct = 0
        st.info(f"Great job! You've advanced to level {st.session_state.level}!")

    st.experimental_rerun()
