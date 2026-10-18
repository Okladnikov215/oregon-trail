import sys
import subprocess
from pathlib import Path

def process_file(py_file):
    """ÐŸÐ¾Ð»Ð½Ñ‹Ð¹ Ñ†Ð¸ÐºÐ» Ð¾Ð±Ñ€Ð°Ð±Ð¾Ñ‚ÐºÐ¸ Ð¾Ð´Ð½Ð¾Ð³Ð¾ .py Ñ„Ð°Ð¹Ð»Ð°."""
    print(f"\n{'='*60}")
    print(f"Processing: {py_file}")
    print('='*60)
    
    # 1. Ð˜Ð·Ð²Ð»ÐµÑ‡ÐµÐ½Ð¸Ðµ ÑÑ‚Ñ€Ð¾Ðº
    result = subprocess.run(
        [sys.executable, "scripts/extract_strings.py", str(py_file)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Extract failed: {result.stderr}")
        return False
    print(result.stdout)
    
    # 2. ÐŸÐµÑ€ÐµÐ²Ð¾Ð´
    strings_file = py_file.with_suffix('.strings.json')
    if not strings_file.exists():
        print("No strings found, skipping")
        return True
    
    result = subprocess.run(
        [sys.executable, "scripts/translate_strings.py", str(strings_file)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Translate failed: {result.stderr}")
        return False
    print(result.stdout)
    
    # 3. ÐŸÑ€Ð¸Ð¼ÐµÐ½ÐµÐ½Ð¸Ðµ Ð¿ÐµÑ€ÐµÐ²Ð¾Ð´Ð°
    result = subprocess.run(
        [sys.executable, "scripts/apply_translation.py", str(py_file)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Apply failed: {result.stderr}")
        return False
    print(result.stdout)
    
    # 4. ÐžÑ‡Ð¸ÑÑ‚ÐºÐ° Ð²Ñ€ÐµÐ¼ÐµÐ½Ð½Ñ‹Ñ… Ñ„Ð°Ð¹Ð»Ð¾Ð²
    strings_file.unlink()
    py_file.with_suffix('.strings.translated.json').unlink()
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: translate_project.py <directory>")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    py_files = list(directory.rglob("*.py"))
    py_files = [f for f in py_files if '.venv' not in str(f)]
    
    print(f"Found {len(py_files)} Python files")
    
    success = []
    failed = []
    
    for py_file in py_files:
        if process_file(py_file):
            success.append(py_file)
        else:
            failed.append(py_file)
    
    print(f"\n{'='*60}")
    print(f"Success: {len(success)}")
    print(f"Failed: {len(failed)}")
    if failed:
        print("Failed files:")
        for f in failed:
            print(f"  - {f}")
