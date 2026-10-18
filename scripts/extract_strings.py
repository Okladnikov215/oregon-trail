"""
Extract hardcoded strings from Python files and replace with _() calls.

Usage:
    python scripts/extract_strings.py [directory]
"""
import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def find_target_strings(tree: ast.AST, source: str) -> List[Tuple[ast.AST, str]]:
    """
    Находит строки, которые нужно перевести.
    
    Ищет строки в:
    - print("...")
    - input("...")
    - raise Exception("...")
    """
    targets = []
    
    class StringFinder(ast.NodeVisitor):
        def visit_Call(self, node):
            # print("text") или input("text")
            if isinstance(node.func, ast.Name) and node.func.id in ('print', 'input'):
                if node.args and isinstance(node.args[0], ast.Constant):
                    if isinstance(node.args[0].value, str):
                        targets.append((node.args[0], node.args[0].value))
            self.generic_visit(node)
        
        def visit_Raise(self, node):
            # raise Exception("message")
            if node.exc:
                if isinstance(node.exc, ast.Call):
                    if node.exc.args and isinstance(node.exc.args[0], ast.Constant):
                        if isinstance(node.exc.args[0].value, str):
                            targets.append((node.exc.args[0], node.exc.args[0].value))
            self.generic_visit(node)
    
    StringFinder().visit(tree)
    return targets


def extract_from_file(file_path: Path) -> Tuple[Dict[str, str], str]:
    """Извлекает строки из одного файла."""
    # Используем utf-8-sig чтобы автоматически удалить BOM если есть
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        source = f.read()
    
    tree = ast.parse(source)
    targets = find_target_strings(tree, source)
    
    # Создаём словарь переводов (ключ = оригинальная строка)
    translations = {}
    
    # Заменяем строки на вызовы _()
    modified_source = source
    lines = modified_source.split('\n')
    
    # Сортируем по позиции в обратном порядке, чтобы не сбить индексы
    targets.sort(key=lambda x: (x[0].lineno, x[0].col_offset), reverse=True)
    
    for node, text in targets:
        if len(text) < 2 or text.isspace():
            continue
        
        # Добавляем в словарь
        translations[text] = text
        
        # Находим строку с этим узлом
        line_idx = node.lineno - 1
        if line_idx < len(lines):
            line = lines[line_idx]
            
            # Пробуем заменить с двойными кавычками
            old_pattern = f'"{text}"'
            new_pattern = f'_("{text}")'
            
            if old_pattern in line:
                lines[line_idx] = line.replace(old_pattern, new_pattern, 1)
                continue
            
            # Пробуем с одинарными кавычками
            old_pattern = f"'{text}'"
            new_pattern = f"_('{text}')"
            if old_pattern in line:
                lines[line_idx] = line.replace(old_pattern, new_pattern, 1)
    
    modified_source = '\n'.join(lines)
    return translations, modified_source


def should_skip(file_path: Path) -> bool:
    """Проверяет, нужно ли пропустить файл."""
    path_str = str(file_path)
    
    # Пропускаем служебные директории
    skip_dirs = ['.venv', '__pycache__', 'scripts', 'i18n', '.git', 'node_modules']
    for skip_dir in skip_dirs:
        if skip_dir in path_str:
            return True
    
    return False


def process_directory(directory: Path):
    """Обрабатывает все .py файлы в директории."""
    all_translations = {}
    processed_files = []
    
    py_files = list(directory.rglob("*.py"))
    py_files = [f for f in py_files if not should_skip(f)]
    
    print(f"Found {len(py_files)} Python files")
    
    for file_path in py_files:
        print(f"\nProcessing: {file_path}")
        
        try:
            translations, modified_source = extract_from_file(file_path)
            
            if translations:
                all_translations.update(translations)
                
                # Сохраняем резервную копию
                backup_path = file_path.with_suffix('.py.backup')
                file_path.rename(backup_path)
                
                # Сохраняем изменённый файл (без BOM)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_source)
                
                processed_files.append(file_path)
                print(f"  Extracted {len(translations)} strings")
            else:
                print(f"  No strings found")
        
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Сохраняем словарь переводов
    i18n_dir = directory / "i18n"
    i18n_dir.mkdir(exist_ok=True)
    
    en_json = i18n_dir / "en.json"
    with open(en_json, 'w', encoding='utf-8') as f:
        json.dump(all_translations, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Total unique strings: {len(all_translations)}")
    print(f"Saved to: {en_json}")
    print(f"Modified files: {len(processed_files)}")
    
    return processed_files


if __name__ == "__main__":
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    process_directory(directory)
