import json
import sys
import time
from pathlib import Path
from openai import OpenAI

def translate_string(client, model, text, lang="Russian"):
    """ÐŸÐµÑ€ÐµÐ²Ð¾Ð´Ð¸Ñ‚ Ð¾Ð´Ð½Ñƒ ÑÑ‚Ñ€Ð¾ÐºÑƒ."""
    prompt = f"""You are a professional game translator for 'Oregon Trail' (1978).

Translate to {lang}. Rules:
- Preserve placeholders exactly: {{}}, {{name}}, %s, %d, {{0}}, {{1}}
- Preserve newlines and escape sequences
- Keep game terminology consistent
- Do NOT translate technical code or variable names inside {{}} in f-strings
- Return ONLY the translation, no explanations

Source: {text}"""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error translating: {e}")
        return text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: translate_strings.py <file.strings.json>")
        sys.exit(1)
    
    json_path = Path(sys.argv[1])
    with open(json_path, 'r', encoding='utf-8') as f:
        strings = json.load(f)
    
    client = OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio"
    )
    
    # ÐŸÐ¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ Ð¸Ð¼Ñ Ð¼Ð¾Ð´ÐµÐ»Ð¸
    models = client.models.list()
    model_id = models.data[0].id
    
    print(f"Translating {len(strings)} strings using {model_id}")
    
    translated = {}
    for i, (key, text) in enumerate(strings.items(), 1):
        print(f"[{i}/{len(strings)}] {text[:60]}...")
        translated[key] = translate_string(client, model_id, text)
        time.sleep(0.2)
    
    out_path = json_path.with_name(json_path.stem + ".translated.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)
    
    print(f"Translated to {out_path}")
