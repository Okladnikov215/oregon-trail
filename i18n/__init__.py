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

# Глобальное состояние
_current_language = "en"
_translations = {}
_base_language = "en"  # Базовый язык (оригинал)


def load_language(lang_code: str):
    """Загружает переводы для указанного языка."""
    global _current_language, _translations
    
    i18n_dir = Path(__file__).parent
    lang_file = i18n_dir / f"{lang_code}.json"
    
    if not lang_file.exists():
        print(f"Warning: Language file not found: {lang_file}")
        _translations = {}
        _current_language = lang_code
        return
    
    with open(lang_file, 'r', encoding='utf-8') as f:
        _translations = json.load(f)
    
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
    """Returns list of available language codes."""
    i18n_dir = Path(__file__).parent
    languages = []
    
    for json_file in i18n_dir.glob("*.json"):
        languages.append(json_file.stem)
    
    return sorted(languages)


# Автоматическая загрузка английского при импорте
load_language("en")
