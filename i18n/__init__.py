"""
Internationalization module for Oregon Trail.

Usage:
    from i18n import _
    
    print(_("You have died of dysentery."))
    name = input(_("What is your name? "))
"""
import json
import os
from pathlib import Path

# Global state
_current_language = "en"
_translations = {}
_base_language = "en"  # Base language (original)


def load_language(lang_code: str):
    """Loads translations for the specified language."""
    global _current_language, _translations
    
    i18n_dir = Path(__file__).parent
    lang_file = i18n_dir / f"{lang_code}.json"
    
    if not lang_file.exists():
        print(f"Warning: Language file not found: {lang_file}")
        _translations = {}
        _current_language = lang_code
        return
    
    with open(lang_file, 'r', encoding='utf-8') as f:
        try:
            _translations = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in language file: {lang_file}")
            _translations = {}
    
    _current_language = lang_code


def _(text: str) -> str:
    """
    Translate a string.
    
    Args:
        text: Original string in base language (English)
    
    Returns:
        Translated string, or original if translation not found
    """
    if _current_language == _base_language:
        return text
    
    return _translations.get(text, text)


def get_language() -> str:
    """Returns current language code."""
    return _current_language


def set_language(lang_code: str):
    """Sets current language and loads translations."""
    load_language(lang_code)


def get_available_languages() -> list[str]:
    """Returns list of available language codes found in the i18n directory."""
    i18n_dir = Path(__file__).parent
    languages = []
    
    for json_file in i18n_dir.glob("*.json"):
        # Ensure it's a valid language file (e.g., en.json, ru.json)
        if json_file.is_file():
            languages.append(json_file.stem)
            
    return sorted(languages)


# Automatically load English on import
load_language("en")
