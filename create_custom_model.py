def create_custom_model():
    print("\n🎨 " + ("Create your own anime girl" if lang == "en" else "Создание собственной аниме-девочки"))
    model_name = input("🧸 " + ("Name: " if lang == "en" else "Имя модели: "))
    prefix = input("🔤 " + ("Prefix (e.g. 'nya~'): " if lang == "en" else "Приставка-фраза (например, 'ня~'): "))
    style = []
    print("💬 " + ("Enter phrases (type 'stop' to finish):" if lang == "en" else "Вводи фразы (напиши 'стоп' чтобы закончить):"))
    while True:
        line = input("> ")
        if line.lower() in ["stop", "стоп"]:
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