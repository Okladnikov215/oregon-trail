import json

with open("i18n/en.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Удаляем проблемную строку
key_to_remove = "AFTER g_vars.GOAL_IN_MILES LONG MILES---HOORAY !!!!!"
if key_to_remove in data:
    del data[key_to_remove]
    print(f"Removed: {key_to_remove}")

# Добавляем правильные ключи
data["AFTER"] = "AFTER"
data["LONG MILES---HOORAY !!!!!"] = "LONG MILES---HOORAY !!!!!"

with open("i18n/en.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Fixed en.json")
