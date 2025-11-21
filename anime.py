from utils import load_custom_models, save_custom_model, get_all_characters, generate_response, load_shared_history, add_to_shared_history, load_user_name, save_user_name

# Load or ask for user name
name = load_user_name()
if not name:
    name = input("📝 Enter your name: ")
    save_user_name(name)

load_shared_history()  # Load global history for better responses

def create_custom_model():
    print("\n🎨 Create your own character")
    model_name = input("🧸 Name: ")
    prefix = input("🔤 Prefix (e.g. 'nya~'): ")
    style = []
    print("💬 Enter phrases (type 'stop' to finish):")
    while True:
        line = input("> ")
        if line.lower() == "stop":
            break
        style.append(line)
    custom_id = f"custom_{len(load_custom_models())+1}"
    model = {
        "name": model_name,
        "prefix": prefix,
        "style": style
    }
    save_custom_model(custom_id, model)
    return model

def choose_character():
    characters = get_all_characters()
    keys = list(characters.keys())
    print("\n🎌 Choose your character:")
    for i, key in enumerate(keys, 1):
        custom_marker = " 🛠️" if key.startswith("custom_") else ""
        print(f"{i}. {characters[key]['name']}{custom_marker}")
    print(f"{len(keys)+1}. ✨ Create your own")

    choice = int(input("> ")) - 1
    if choice == len(keys):
        return create_custom_model()
    else:
        return characters[keys[choice]]

char = choose_character()

print(f"\n✨ Now chatting with {char['name']}! Type 'exit' to stop.\n")
while True:
    msg = input("You: ")
    if msg.lower() == "exit":
        print(f"{char['name']}: See you soon!")
        break
    response = generate_response(msg, char, name)
    print(f"{char['name']}: {response}")
    add_to_shared_history(msg, char['name'], response)  # Add to shared brain
