#!/usr/bin/env python3
"""
Скрипт для уменьшения полей в EPUB книгах для Kindle
Использование: 
  python3 modify_epub_margins.py book.epub [book2.epub ...]  # конкретные файлы
  python3 modify_epub_margins.py --all                       # все .epub в текущей папке
  python3 modify_epub_margins.py                             # все .epub в текущей папке
  python3 modify_epub_margins.py --margin 30                 # изменить размер полей
"""

import sys
import os
import zipfile
import tempfile
import shutil
import glob
from pathlib import Path

def get_margin_css(margin_size=20):
    """Генерировать CSS код для уменьшения полей"""
    return f"""
/* Уменьшенные поля для Kindle */
html, body {{
    margin-left: -{margin_size}px !important;
    margin-right: -{margin_size}px !important;
    padding: 0 !important;
}}
"""

def find_css_file(temp_dir):
    """Найти основной CSS файл в распакованном EPUB"""
    possible_paths = [
        "OPS/style.css",
        "OEBPS/style.css", 
        "styles/style.css",
        "css/style.css"
    ]
    
    for path in possible_paths:
        css_path = os.path.join(temp_dir, path)
        if os.path.exists(css_path):
            return css_path
    
    return None

def process_epub(epub_path, margin_size=20):
    """Обработать один EPUB файл"""
    epub_path = Path(epub_path)
    output_path = epub_path.parent / f"{epub_path.stem}-upgrade.epub"
    
    print(f"Обрабатываю: {epub_path} (поля: -{margin_size}px)")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Распаковать EPUB
        with zipfile.ZipFile(epub_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Найти CSS файл
        css_file = find_css_file(temp_dir)
        
        if css_file is None:
            print("Предупреждение: CSS файл не найден, создаю новый")
            # Создать CSS файл если его нет
            ops_dir = os.path.join(temp_dir, "OPS")
            os.makedirs(ops_dir, exist_ok=True)
            css_file = os.path.join(ops_dir, "style.css")
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write("/* Автоматически созданный CSS */\n")
        
        # Добавить CSS для уменьшения полей
        with open(css_file, 'a', encoding='utf-8') as f:
            f.write(get_margin_css(margin_size))
        
        # Создать новый EPUB файл
        with zipfile.ZipFile(output_path, 'w') as zip_out:
            # Сначала добавить mimetype без сжатия
            mimetype_path = os.path.join(temp_dir, 'mimetype')
            if os.path.exists(mimetype_path):
                zip_out.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
            
            # Затем добавить все остальные файлы
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file == 'mimetype':
                        continue  # Уже добавлен
                    
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_dir)
                    zip_out.write(file_path, arc_path, compress_type=zipfile.ZIP_DEFLATED)
    
    print(f"Готово: {output_path}")

def get_epub_files():
    """Получить все .epub файлы в текущей директории"""
    return glob.glob("*.epub")

def main():
    epub_files = []
    margin_size = 20  # По умолчанию
    
    # Парсинг аргументов
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg == "--help" or arg == "-h":
            print("Использование:")
            print("  python3 modify_epub_margins.py                    # все .epub в текущей папке")
            print("  python3 modify_epub_margins.py --all              # все .epub в текущей папке")
            print("  python3 modify_epub_margins.py book.epub          # конкретный файл")
            print("  python3 modify_epub_margins.py *.epub             # по маске")
            print("  python3 modify_epub_margins.py --margin 30        # изменить размер полей (по умолчанию 20)")
            print("  python3 modify_epub_margins.py --margin 15 *.epub # размер полей + файлы")
            sys.exit(0)
        
        elif arg == "--margin":
            if i + 1 < len(args):
                try:
                    margin_size = int(args[i + 1])
                    i += 1  # Пропустить следующий аргумент
                except ValueError:
                    print(f"Ошибка: '{args[i + 1]}' не является числом")
                    sys.exit(1)
            else:
                print("Ошибка: после --margin должно быть указано число")
                sys.exit(1)
        
        elif arg == "--all":
            pass  # Обработаем ниже
        
        else:
            # Поддержка масок типа *.epub
            if "*" in arg:
                matched_files = glob.glob(arg)
                epub_files.extend([f for f in matched_files if f.lower().endswith('.epub')])
            else:
                epub_files.append(arg)
        
        i += 1
    
    # Если нет файлов в аргументах или передан --all, обработать все .epub в папке
    if not epub_files or "--all" in sys.argv:
        epub_files = get_epub_files()
        if not epub_files:
            print("В текущей папке не найдено .epub файлов")
            sys.exit(1)
        print(f"Найдено {len(epub_files)} .epub файлов в текущей папке")
    
    if not epub_files:
        print("Не указаны файлы для обработки")
        print("Используйте --help для справки")
        sys.exit(1)
    
    # Убрать дубликаты и отфильтровать только существующие .epub файлы
    unique_files = []
    for epub_file in set(epub_files):
        if os.path.exists(epub_file) and epub_file.lower().endswith('.epub'):
            # Пропустить уже обработанные файлы
            if not epub_file.endswith('-upgrade.epub'):
                unique_files.append(epub_file)
            else:
                print(f"Пропускаю уже обработанный файл: {epub_file}")
        else:
            print(f"Пропускаю: {epub_file} (не найден или не .epub файл)")
    
    if not unique_files:
        print("Нет файлов для обработки")
        sys.exit(1)
    
    print(f"Будет обработано {len(unique_files)} файлов с полями -{margin_size}px:")
    for f in unique_files:
        print(f"  - {f}")
    print()
    
    # Обработать файлы
    success_count = 0
    for epub_file in unique_files:
        try:
            process_epub(epub_file, margin_size)
            success_count += 1
        except Exception as e:
            print(f"Ошибка при обработке {epub_file}: {e}")
    
    print(f"\nГотово! Успешно обработано {success_count} из {len(unique_files)} файлов")

if __name__ == "__main__":
    main()