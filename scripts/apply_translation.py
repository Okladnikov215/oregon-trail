import json
import sys
import py_compile
from pathlib import Path

def replace_strings(source_path, translated_path, output_path):
    """Ð—Ð°Ð¼ÐµÐ½ÑÐµÑ‚ ÑÑ‚Ñ€Ð¾ÐºÐ¸ Ð² Ð¸ÑÑ…Ð¾Ð´Ð½Ð¾Ð¼ ÐºÐ¾Ð´Ðµ Ð½Ð° Ð¿ÐµÑ€ÐµÐ²ÐµÐ´Ñ‘Ð½Ð½Ñ‹Ðµ."""
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(translated_path, 'r', encoding='utf-8') as f:
        translated = json.load(f)
    
    # Ð˜Ð·Ð²Ð»ÐµÐºÐ°ÐµÐ¼ Ð¾Ñ€Ð¸Ð³Ð¸Ð½Ð°Ð»ÑŒÐ½Ñ‹Ðµ ÑÑ‚Ñ€Ð¾ÐºÐ¸
    source_strings_path = source_path.with_suffix('.strings.json')
    with open(source_strings_path, 'r', encoding='utf-8') as f:
        original_strings = json.load(f)
    
    # Ð—Ð°Ð¼ÐµÐ½ÑÐµÐ¼ Ð¿Ð¾ÑÑ‚Ñ€Ð¾Ñ‡Ð½Ð¾
    for key, original in original_strings.items():
        if key in translated:
            replacement = translated[key]
            # Ð˜ÑÐ¿Ð¾Ð»ÑŒÐ·ÑƒÐµÐ¼ repr Ð´Ð»Ñ Ð¿Ñ€Ð°Ð²Ð¸Ð»ÑŒÐ½Ð¾Ð³Ð¾ ÑÐºÑ€Ð°Ð½Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð¸Ñ
            # ÐÐ¾ Ñ€Ð°Ð±Ð¾Ñ‚Ð°ÐµÐ¼ Ñ raw ÑÑ‚Ñ€Ð¾ÐºÐ°Ð¼Ð¸, ÑÐ¾Ñ…Ñ€Ð°Ð½ÑÑ Ð¾Ñ€Ð¸Ð³Ð¸Ð½Ð°Ð»ÑŒÐ½Ñ‹Ðµ ÐºÐ°Ð²Ñ‹Ñ‡ÐºÐ¸
            content = content.replace(original, replacement, 1)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # ÐŸÑ€Ð¾Ð²ÐµÑ€ÑÐµÐ¼ ÑÐ¸Ð½Ñ‚Ð°ÐºÑÐ¸Ñ
    try:
        py_compile.compile(str(output_path), doraise=True)
        print(f"Syntax OK: {output_path}")
        return True
    except py_compile.PyCompileError as e:
        print(f"Syntax error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: apply_translation.py <file.py>")
        sys.exit(1)
    
    source_path = Path(sys.argv[1])
    translated_path = source_path.with_suffix('.strings.translated.json')
    output_path = source_path.with_suffix('.py.ru')
    
    if not translated_path.exists():
        print(f"Not found: {translated_path}")
        sys.exit(1)
    
    if replace_strings(source_path, translated_path, output_path):
        # ÐŸÐµÑ€ÐµÐ·Ð°Ð¿Ð¸ÑÑ‹Ð²Ð°ÐµÐ¼ Ð¾Ñ€Ð¸Ð³Ð¸Ð½Ð°Ð»
        output_path.replace(source_path)
        print(f"Updated: {source_path}")
    else:
        print(f"FAILED: keeping original")
        sys.exit(1)
