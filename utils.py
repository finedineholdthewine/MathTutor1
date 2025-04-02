# utils.py
import random
import json
import os

def generate_problem(level):
    """
    Generates a math problem based on the level.
    Level 1: Simple addition/subtraction.
    Level 2: Multiplication/division with an integer result.
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
        if random.choice([True, False]):
            a = random.randint(2, 12)
            b = random.randint(2, 12)
            product = a * b
            divisors = [d for d in range(1, product + 1) if product % d == 0]
            c = random.choice(divisors)
            expr = f"{a} * {b} / {c}"
            answer = product // c
        else:
            b = random.randint(2, 12)
            a = b * random.randint(1, 12)
            c = random.randint(1, 12)
            expr = f"{a} / {b} * {c}"
            answer = (a // b) * c
        return expr, answer

    else:
        expr = "2 + (3 - 1)"
        answer = 4
        return expr, answer

def save_progress(state, filename):
    """
    Saves selected progress data to a JSON file.
    """
    progress_keys = ['name', 'questions_answered', 'correct_answers', 'current_streak', 'current_level']
    progress_data = {k: state.get(k) for k in progress_keys}
    with open(filename, 'w') as f:
        json.dump(progress_data, f)

def load_progress(filename):
    """
    Loads progress data from a JSON file if it exists.
    Returns the progress data as a dict, or None if the file doesn't exist.
    """
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            progress_data = json.load(f)
        return progress_data
    else:
        return None
