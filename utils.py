# utils.py
import random
import json
import os

def generate_problem(level):
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

    elif level == 3:
        # Multi-step problem: a * (b + c) - d
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        c = random.randint(1, 10)
        d = random.randint(1, 10)
        expr = f"{a} * ({b} + {c}) - {d}"
        answer = a * (b + c) - d
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
        
        
def load_high_scores(filename="high_scores.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return []

def save_high_score(name, score, filename="high_scores.json"):
    scores = load_high_scores(filename)
    scores.append({"name": name, "score": score})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    with open(filename, "w") as f:
        json.dump(scores, f)

def get_top_scores(filename="high_scores.json"):
    scores = load_high_scores(filename)
    return scores[:10]

def load_player_data(filename="players.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

def save_player_data(name, filename="players.json"):
    data = load_player_data(filename)
    data[name] = data.get(name, 0) + 1
    with open(filename, "w") as f:
        json.dump(data, f)

def get_player_greeting(name, filename="players.json"):
    data = load_player_data(filename)
    if name in data:
        return f"Welcome back, {name}! Let's see if you can beat your best today!"
    else:
        return f"Nice to meet you, {name}! Let's have some fun learning math!"