import json
import random
import os
from character import CHARACTERS
import re
import webbrowser
import subprocess
import time
try:
    import psutil
except ImportError:
    psutil = None

from links_config import links

# User name persistence
def load_user_name():
    if os.path.exists("user_name.json"):
        with open("user_name.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("name", "")
    return ""

def save_user_name(name):
    with open("user_name.json", "w", encoding="utf-8") as f:
        json.dump({"name": name}, f, ensure_ascii=False, indent=2)

def open_link(phrase):
    for key, url in links.items():
        if key.lower() in phrase.lower():
            webbrowser.open(url)
            return f"Opening {key}..."
    return "Link not found."

# Shared brain: global chat history
shared_history = []

def load_shared_history():
    global shared_history
    if os.path.exists("shared_history.json"):
        with open("shared_history.json", "r", encoding="utf-8") as f:
            shared_history = json.load(f)
    else:
        shared_history = []

def save_shared_history():
    with open("shared_history.json", "w", encoding="utf-8") as f:
        json.dump(shared_history, f, ensure_ascii=False, indent=2)

def add_to_shared_history(user_msg, char_name, response):
    shared_history.append({
        "user": user_msg,
        "char": char_name,
        "reply": response
    })
    if len(shared_history) > 50:  # limit history
        shared_history.pop(0)
    save_shared_history()

def load_custom_models():
    if os.path.exists("models.json"):
        with open("models.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_custom_model(model_id, model_data):
    models = load_custom_models()
    models[model_id] = model_data
    with open("models.json", "w", encoding="utf-8") as f:
        json.dump(models, f, ensure_ascii=False, indent=2)

def create_custom_model(model_name, prefix, style):
    custom_id = f"custom_{len(load_custom_models())+1}"
    model = {
        "name": model_name,
        "prefix": prefix,
        "style": style
    }
    save_custom_model(custom_id, model)
    return custom_id, model

def get_all_characters():
    base_characters = CHARACTERS
    custom_models = load_custom_models()
    all_characters = {}
    all_characters.update(base_characters)
    all_characters.update(custom_models)
    return all_characters

# Self-learning: Add new phrases to character's style based on history
def self_learn_from_history(char_key, user_input, response):
    models = load_custom_models()
    if char_key in models:
        if user_input.lower().startswith("teach me"):
            new_phrase = user_input[9:].strip()  # Remove "teach me "
            models[char_key]["style"].append(new_phrase)
            save_custom_model(char_key, models[char_key])
            return "Learned that! " + random.choice(["Got it~", "Thanks for teaching me!", "Cool, I remember now."])
    # For all characters, learn from positive feedback
    if "good" in user_input.lower() or "like" in user_input.lower():
        base_style = CHARACTERS.get(char_key, {}).get("style", [])
        if base_style:
            return random.choice(base_style).format(name="") + " Thanks!"
    return None

# Device control functions
def control_device(command):
    lower = command.lower()
    if "shutdown" in lower or "power off" in lower:
        return "Sorry, I can't shut down the system for safety reasons."
    elif "restart" in lower:
        return "Restarting system..."
        # subprocess.run(["shutdown", "/r", "/t", "1"])  # Windows restart
    elif "open notepad" in lower:
        try:
            subprocess.Popen(["notepad"])
            return "Opened Notepad!"
        except:
            return "Sorry, couldn't open Notepad."
    elif "open calculator" in lower:
        try:
            subprocess.Popen(["calc"])
            return "Opened Calculator!"
        except:
            return "Sorry, couldn't open Calculator."
    elif "run" in lower:
        # Allow running simple commands, but safely
        return "Sorry, for safety, I can only run predefined commands."
    else:
        return "I don't know how to control that yet."

# Game functions
import random as rand

game_state = None  # To track current game

def play_game(user_input, char, name):
    global game_state
    lower = user_input.lower()

    if "play" in lower:
        if "guess number" in lower or "угадай число" in lower:
            game_state = {"type": "guess_number", "number": random.randint(1, 100), "attempts": 0}
            return f"Let's play! I thought of a number between 1 and 100. Guess it, {name}!"
        elif "rock paper scissors" in lower or "камень ножницы бумага" in lower:
            game_state = {"type": "rps"}
            return "Let's play Rock-Paper-Scissors! Say 'rock', 'paper', or 'scissors'."
        elif "baryshnya-krestyanka" in lower or "барышня-крестьянка" in lower:
            game_state = {"type": "baryshnya", "role": random.choice(["baron", "baroness"]), "round": 0}
            return f"Let's play Baryshnya-Krestyanka! I am {game_state['role']}. You be the other. Ask a question!"
        else:
            return "What game do you want to play? Options: guess number, rock paper scissors, or baryshnya-krestyanka."
    elif game_state:
        if game_state["type"] == "guess_number":
            try:
                guess = int(user_input)
                game_state["attempts"] += 1
                if guess < game_state["number"]:
                    return "Higher!"
                elif guess > game_state["number"]:
                    return "Lower!"
                else:
                    game_state = None
                    return f"Yes! It was {game_state['number']}. You guessed in {game_state['attempts']} attempts. You're amazing, {name}!"
            except ValueError:
                return "Please guess a number between 1 and 100."
        elif game_state["type"] == "rps":
            choices = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
            if user_input.lower() in choices:
                ai_choice = random.choice(list(choices.keys()))
                user = user_input.lower()
                if choices[user] == ai_choice:
                    result = "You win!"
                elif choices[ai_choice] == user:
                    result = "I win!"
                else:
                    result = "Draw!"
                game_state = None
                return f"I chose {ai_choice}. {result}"
            else:
                return "Say 'rock', 'paper', or 'scissors'."
        elif game_state["type"] == "baryshnya":
            # Simple role-play
            if "who" in lower or "what" in lower or "where" in lower:
                answers = [
                    "I am from a mythical land.",
                    "The baron owns many lands.",
                    "The baron's daughter is beautiful.",
                    "I love adventures!"
                ]
                game_state["round"] += 1
                if game_state["round"] > 5:
                    game_state = None
                    return "Game over! Did you figure it out?"
                return random.choice(answers)
            else:
                return "Ask a question starting with who, what, or where!"
    return None

# System monitoring functions
def get_system_stats():
    if not psutil:
        return "Monitoring not available (install psutil)."
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return f"CPU: {cpu}%, RAM: {mem.percent}%, Disk: {disk.percent}%."

def search_and_open(query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    return f"Searching for '{query}'..."

def get_weather(city):
    # Mock weather - in real app, use API
    weathers = ["Sunny", "Rainy", "Cloudy", "Snowy"]
    temp = rand.randint(0, 30)
    return f"Weather in {city}: {rand.choice(weathers)}, {temp}°C."

def get_news():
    # Mock news
    topics = ["Tech breakthrough", "New anime release", "Sports victory", "Health tips"]
    return f"Top news: {rand.choice(topics)}. Check a news site for more."

# Enhanced device control
def execute_command_safe(cmd):
    safe_cmds = {
        "ipconfig": "Displays network info.",
        "dir": "Lists directory contents on Windows.",
        "whoami": "Shows current user.",
    }
    if cmd in safe_cmds:
        try:
            result = subprocess.check_output(cmd, shell=True, text=True)
            return f"{safe_cmds[cmd]}\n{result[:200]}..."  # Limit output
        except:
            return "Command failed or not safe."
    return "Command not allowed for safety."

# Enhanced generate_response with more helpers
def generate_response(user_input, char, name):
    lower = user_input.lower()

    # Check for games
    game_response = play_game(user_input, char, name)
    if game_response:
        return game_response

    # Check for system monitoring
    if "system stats" in lower or "pc load" in lower or "cpu" in lower:
        return get_system_stats()

    # Check for search
    if lower.startswith("search "):
        query = user_input[7:]
        return search_and_open(query)

    # Check for weather
    if "weather" in lower:
        city = "Москва"  # Default, or parse after "weather in"
        return get_weather(city)

    # Check for news
    if "news" in lower:
        return get_news()

    # Check for safe commands
    if lower.startswith("run "):
        cmd = user_input[4:]
        return execute_command_safe(cmd)

    # Check for learning commands
    if lower.startswith("teach"):
        learned = self_learn_from_history(list(get_all_characters().keys())[0] if list(get_all_characters().keys()) else "neko", user_input, "")
        if learned:
            return learned

    # Help with questions
    if "what is" in lower or "how to" in lower or "why" in lower:
        return "As your helper, I'll try to explain: {user_input}. But I'm still learning! Search online for details."
    elif "time" in lower:
        current_time = time.strftime("%H:%M:%S")
        return f"The current time is {current_time}."
    elif "date" in lower:
        current_date = time.strftime("%Y-%m-%d")
        return f"Today's date is {current_date}."

    # Device control
    if "open" in lower and not any(word in lower for word in ["youtube", "github", "google"]):  # Already handled
        device_response = control_device(user_input)
        if device_response:
            return device_response

    # Check for open link requests (existing)
    if "open" in lower:
        link_response = open_link(user_input)
        if link_response != "Link not found.":
            return link_response

    # Enhanced patterns for better conversation
    if any(word in lower for word in ["how are you", "how do you do"]):
        return random.choice([f"I'm doing great, {name}! How about you?", "Fantastic! What's up with you?", "Good! Always ready to chat."])
    elif "joke" in lower:
        jokes = ["Why don't scientists trust atoms? Because they make up everything!", f"{name}, you are the punchline of my jokes!", "Knock knock. Who's there? {char['name']}!"]
        return random.choice(jokes)
    elif "story" in lower:
        return "Once upon a time, in a digital world... Okay, I need better stories. Tell me one first!"

    # Check for known patterns (existing)
    if "hi" in lower or "hello" in lower:
        return random.choice([f"Hi {name}~", "Hello there!", "Hehe, welcome back~"])
    elif "love" in lower:
        return random.choice(["W-what? I mean... maybe I do...", f"I love you too, {name}~"])
    elif "sad" in lower:
        return random.choice(["Don't be sad, I'm here.", f"Cheer up, {name}!"])

    # Check shared history for similar conversations (existing)
    relevant_history = [entry for entry in shared_history if re.search(r'\b' + re.escape(user_input.split()[0]) + r'\b', entry["user"], re.IGNORECASE)]
    if relevant_history:
        last_reply = relevant_history[-1]["reply"]
        return last_reply.replace("?", "!").replace(".", ",")

    return random.choice([f"{phrase.format(name=name)} {char['prefix']}" for phrase in char["style"]])
