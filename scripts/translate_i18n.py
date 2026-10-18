"""Batch-translate i18n/en.json to target language via LM Studio."""
import json
import re
import sys
import time
from pathlib import Path
from openai import OpenAI

BATCH_SIZE = 12
PLACEHOLDER = re.compile(r"\{[^{}]*\}|%[sdfr]|%\(.*?\)s")


def same_placeholders(original: str, translated: str) -> bool:
    """Проверяет, что плейсхолдеры не потерялись при переводе."""
    return sorted(PLACEHOLDER.findall(original)) == sorted(PLACEHOLDER.findall(translated))


def translate_batch(client, model, batch: dict, lang: str) -> dict:
    """Переводит батч строк за один запрос."""
    keys = list(batch.keys())
    lines = [f"{i}. {batch[k]}" for i, k in enumerate(keys, 1)]
    payload = "\n".join(lines)

    prompt = f"""You are translating the classic game 'Oregon Trail' (1978).

Translate the numbered strings below to {lang}.
Rules:
- Preserve placeholders exactly: {{}}, {{name}}, %s, %d, {{0}}, {{1}}
- Keep newlines and punctuation
- Maintain 19th century American frontier tone
- Output exactly {len(keys)} lines, one per input, preserving numbering

Input:
{payload}

Output:"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024,
    )

    text = response.choices[0].message.content.strip()
    results = {}

    # Парсим ответ: ожидаем строки вида "1. перевод"
    translated_lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    for i, key in enumerate(keys):
        if i < len(translated_lines):
            line = translated_lines[i]
            # Убираем префикс "1. " если модель его вернула
            match = re.match(r"^\d+\.\s*(.*)$", line, re.DOTALL)
            translated = match.group(1) if match else line
            results[key] = translated
        else:
            results[key] = batch[key]  # fallback: оригинал

    return results


def validate_batch(original: dict, translated: dict) -> dict:
    """Отбрасывает переводы с повреждёнными плейсхолдерами."""
    clean = {}
    for key, value in translated.items():
        if key in original and not same_placeholders(original[key], value):
            print(f"  [!] Placeholder mismatch, keeping original: {key[:40]}...")
            clean[key] = original[key]
        else:
            clean[key] = value
    return clean


def main():
    if len(sys.argv) < 2:
        print("Usage: translate_i18n.py <language_name> [lang_code]")
        sys.exit(1)

    lang_name = sys.argv[1]
    lang_code = sys.argv[2] if len(sys.argv) > 2 else lang_name.lower()[:2]

    en_file = Path("i18n/en.json")
    out_file = Path(f"i18n/{lang_code}.json")

    if not en_file.exists():
        print(f"Not found: {en_file}")
        sys.exit(1)

    with open(en_file, "r", encoding="utf-8") as f:
        source = json.load(f)

    # Подгружаем уже переведённое (для возобновления)
    translated = {}
    if out_file.exists():
        with open(out_file, "r", encoding="utf-8") as f:
            translated = json.load(f)

    # Осталось перевести
    remaining = {k: v for k, v in source.items() if k not in translated}

    if not remaining:
        print(f"All {len(source)} strings already translated in {out_file}")
        return

    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    models = client.models.list()
    model_id = models.data[0].id

    print(f"Model: {model_id}")
    print(f"Language: {lang_name}")
    print(f"Total: {len(source)}, already done: {len(translated)}, remaining: {len(remaining)}")

    keys = list(remaining.keys())
    total_batches = (len(keys) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_num in range(total_batches):
        start = batch_num * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(keys))
        batch_keys = keys[start:end]
        batch = {k: remaining[k] for k in batch_keys}

        print(f"\n[{batch_num + 1}/{total_batches}] Translating {len(batch)} strings...")

        try:
            result = translate_batch(client, model_id, batch, lang_name)
            result = validate_batch(batch, result)
            translated.update(result)

            # Сохраняем прогресс после каждого батча
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(translated, f, ensure_ascii=False, indent=2)

            print(f"  Done, saved {len(translated)}/{len(source)}")
            time.sleep(0.5)

        except Exception as exc:
            print(f"  [ERROR] {exc}")
            print("  Progress saved. Re-run to continue from this point.")
            sys.exit(1)

    print(f"\nFinished! Translation saved to {out_file}")


if __name__ == "__main__":
    main()