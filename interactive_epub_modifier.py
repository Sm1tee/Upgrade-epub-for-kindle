#!/usr/bin/env python3
"""
Интерактивный скрипт для модификации EPUB книг для Kindle
Поддерживает уменьшение полей и отключение переносов слов
"""

import sys
import os
import zipfile
import tempfile
import shutil
import glob
from pathlib import Path

# Цвета для консоли
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'  # Сброс цвета

def colored(text, color):
    """Окрасить текст в указанный цвет"""
    return f"{color}{text}{Colors.END}"

def get_margin_css(margin_size=20):
    """CSS для уменьшения полей"""
    return f"""
/* Уменьшенные поля для Kindle */
html, body {{
    margin-left: -{margin_size}px !important;
    margin-right: -{margin_size}px !important;
    padding: 0 !important;
}}
"""

def get_no_hyphenation_css():
    """CSS для отключения переносов слов"""
    return """
/* Отключение переносов слов для Kindle */
* {
    -webkit-hyphens: none !important;
    -moz-hyphens: none !important;
    -ms-hyphens: none !important;
    hyphens: none !important;
    word-break: keep-all !important;
    overflow-wrap: normal !important;
}

p, div, span, td, th {
    -webkit-hyphens: none !important;
    -moz-hyphens: none !important;
    -ms-hyphens: none !important;
    hyphens: none !important;
    word-break: keep-all !important;
}
"""

def get_combined_css(margin_size=20):
    """CSS для уменьшения полей И отключения переносов"""
    return f"""
/* Уменьшенные поля для Kindle */
html, body {{
    margin-left: -{margin_size}px !important;
    margin-right: -{margin_size}px !important;
    padding: 0 !important;
}}

/* Отключение переносов слов для Kindle */
* {{
    -webkit-hyphens: none !important;
    -moz-hyphens: none !important;
    -ms-hyphens: none !important;
    hyphens: none !important;
    word-break: keep-all !important;
    overflow-wrap: normal !important;
}}

p, div, span, td, th {{
    -webkit-hyphens: none !important;
    -moz-hyphens: none !important;
    -ms-hyphens: none !important;
    hyphens: none !important;
    word-break: keep-all !important;
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

def process_epub(epub_path, modification_type, margin_size=20, output_mode="folder", output_dir=None):
    """Обработать один EPUB файл"""
    epub_path = Path(epub_path)
    
    # Определить CSS контент и описание
    if modification_type == "margins":
        css_content = get_margin_css(margin_size)
        description = f"поля -{margin_size}px"
    elif modification_type == "hyphens":
        css_content = get_no_hyphenation_css()
        description = "без переносов"
    elif modification_type == "both":
        css_content = get_combined_css(margin_size)
        description = f"поля -{margin_size}px + без переносов"
    
    # Определить путь для выходного файла
    if output_mode == "replace":
        output_path = epub_path  # Заменить оригинал
    else:  # folder
        output_path = output_dir / epub_path.name
    
    print(colored(f"Обрабатываю: {epub_path} ({description})", Colors.YELLOW))
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Распаковать EPUB
        with zipfile.ZipFile(epub_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Найти CSS файл
        css_file = find_css_file(temp_dir)
        
        if css_file is None:
            print("  CSS файл не найден, создаю новый...")
            # Создать CSS файл если его нет
            ops_dir = os.path.join(temp_dir, "OPS")
            os.makedirs(ops_dir, exist_ok=True)
            css_file = os.path.join(ops_dir, "style.css")
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write("/* Автоматически созданный CSS */\n")
        
        # Добавить CSS модификации
        with open(css_file, 'a', encoding='utf-8') as f:
            f.write(css_content)
        
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
    
    print(colored(f"  Готово: {output_path}", Colors.GREEN))

def get_epub_files():
    """Получить все .epub файлы в текущей директории"""
    files = glob.glob("*.epub")
    # Исключить уже обработанные файлы
    return [f for f in files if not any(suffix in f for suffix in ['-margins.epub', '-no-hyphens.epub', '-enhanced.epub', '-upgrade.epub'])]

def ask_modification_type():
    """Спросить пользователя какую модификацию применить"""
    print("\n" + colored("=" * 50, Colors.BLUE))
    print(colored("           ТИП МОДИФИКАЦИИ", Colors.BLUE + Colors.BOLD))
    print(colored("=" * 50, Colors.BLUE))
    print(colored("1. Уменьшить поля", Colors.WHITE))
    print(colored("2. Отключить переносы слов", Colors.WHITE))
    print(colored("3. Применить обе модификации", Colors.WHITE))
    print(colored("0. Выход", Colors.MAGENTA))
    print(colored("=" * 50, Colors.BLUE))
    
    while True:
        choice = input(colored("\nВыбор [1-3, 0]: ", Colors.CYAN + Colors.BOLD)).strip()
        if choice == "1":
            return "margins"
        elif choice == "2":
            return "hyphens"
        elif choice == "3":
            return "both"
        elif choice == "0":
            return None
        else:
            print(colored("Введите число от 0 до 3", Colors.RED))

def ask_margin_size():
    """Спросить размер полей если нужно"""
    print("\n" + colored("=" * 50, Colors.BLUE))
    print(colored("              РАЗМЕР ПОЛЕЙ", Colors.BLUE + Colors.BOLD))
    print(colored("=" * 50, Colors.BLUE))
    print()
    print("Введите положительное число для уменьшения полей.")
    print()
    print(colored("По умолчанию: 20 (поля уменьшатся на -20px)", Colors.GREEN))
    print()
    print(colored("ВНИМАНИЕ:", Colors.YELLOW + Colors.BOLD) + " Значения больше 20 не рекомендуются,")
    print("т.к. текст может уйти за рамки экрана.")
    print()
    print(colored("Нажмите Enter для значения по умолчанию.", Colors.CYAN))
    print(colored("=" * 50, Colors.BLUE))
    
    while True:
        try:
            size = input(colored("\nВведите число [20]: ", Colors.CYAN + Colors.BOLD)).strip()
            if not size:
                return 20
            return int(size)
        except ValueError:
            print(colored("Введите число", Colors.RED))

def ask_output_mode():
    """Спросить куда сохранять обработанные файлы"""
    print("\n" + "=" * 45)
    print("              СОХРАНЕНИЕ")
    print("=" * 45)
    print("1. В папку 'books-upgrade'")
    print("2. Заменить оригинальные файлы")
    print("0. Назад")
    print("=" * 45)
    
    while True:
        choice = input("\nВыбор [1-2, 0]: ").strip()
        if choice == "1":
            return "folder"
        elif choice == "2":
            return "replace"
        elif choice == "0":
            return None
        else:
            print("Введите 1, 2 или 0")

def ask_file_selection(epub_files):
    """Спросить какие файлы обрабатывать"""
    print(f"\n" + "=" * 50)
    print(f"      НАЙДЕНО {len(epub_files)} EPUB ФАЙЛОВ")
    print("=" * 50)
    
    for i, file in enumerate(epub_files, 1):
        print(f"{i}. {file}")
    
    print("-" * 50)
    print(f"{len(epub_files) + 1}. Обработать все файлы")
    print("0. Назад")
    print("=" * 50)
    
    while True:
        choice = input(f"\nВыбор [1-{len(epub_files) + 1}, 0]: ").strip()
        
        if choice == "0":
            return None
        elif choice == str(len(epub_files) + 1):
            return epub_files
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(epub_files):
                    return [epub_files[index]]
                else:
                    print(f"Введите число от 1 до {len(epub_files) + 1}")
            except ValueError:
                print("Введите число")

def main():
    print("\n" + colored("=" * 60, Colors.CYAN))
    print(colored("              KINDLE EPUB МОДИФИКАТОР", Colors.CYAN + Colors.BOLD))
    print(colored("=" * 60, Colors.CYAN))
    print(colored("   Модификация EPUB файлов для Kindle", Colors.WHITE))
    print(colored("=" * 60, Colors.CYAN))
    
    # Найти EPUB файлы
    epub_files = get_epub_files()
    if not epub_files:
        print("\n" + "=" * 50)
        print("         EPUB файлы не найдены")
        print("   Поместите .epub файлы в текущую папку")
        print("=" * 50)
        sys.exit(1)
    
    while True:
        # Выбор типа модификации
        modification_type = ask_modification_type()
        if modification_type is None:
            print("\nРабота завершена.")
            break
        
        # Выбор размера полей если нужно
        margin_size = 20
        if modification_type in ["margins", "both"]:
            margin_size = ask_margin_size()
        
        # Выбор куда сохранять файлы
        output_mode = ask_output_mode()
        if output_mode is None:
            continue  # Вернуться к выбору модификации
        
        # Предупреждение при замене оригиналов
        if output_mode == "replace":
            print("\n" + colored("=" * 60, Colors.RED))
            print(colored("                    ВНИМАНИЕ!", Colors.RED + Colors.BOLD))
            print(colored("=" * 60, Colors.RED))
            print()
            print(colored("Вы выбрали замену оригинальных файлов!", Colors.YELLOW + Colors.BOLD))
            print()
            print("Это означает:")
            print(colored("• Оригинальные файлы будут БЕЗВОЗВРАТНО изменены", Colors.RED))
            print(colored("• Резервные копии НЕ создаются", Colors.RED))
            print(colored("• Отменить изменения будет НЕВОЗМОЖНО", Colors.RED))
            print()
            print(colored("Рекомендуется выбрать сохранение в папку", Colors.GREEN))
            print(colored("'books-upgrade' для безопасности", Colors.GREEN))
            print(colored("=" * 60, Colors.RED))
            
            confirm_replace = input(colored("\nВы ТОЧНО хотите заменить оригинальные файлы? (yes/no): ", Colors.YELLOW + Colors.BOLD)).strip().lower()
            if confirm_replace not in ['yes', 'да']:
                print(colored("Операция отменена. Возврат к выбору способа сохранения.", Colors.GREEN))
                continue
        
        # Создать папку если нужно
        output_dir = None
        if output_mode == "folder":
            output_dir = Path("books-upgrade")
            output_dir.mkdir(exist_ok=True)
            print(f"Папка создана: {output_dir}")
        
        # Выбор файлов
        selected_files = ask_file_selection(epub_files)
        if selected_files is None:
            continue  # Вернуться к выбору модификации
        
        # Подтверждение
        print(f"\n" + "=" * 50)
        print("              ПОДТВЕРЖДЕНИЕ")
        print("=" * 50)
        
        if modification_type == "margins":
            print(f"Модификация: уменьшение полей на {margin_size}px")
        elif modification_type == "hyphens":
            print("Модификация: отключение переносов слов")
        elif modification_type == "both":
            print(f"Модификация: поля -{margin_size}px + переносы")
        
        if output_mode == "folder":
            print("Сохранение: в папку 'books-upgrade'")
        elif output_mode == "replace":
            print("Сохранение: замена оригинальных файлов")
        
        print(f"Файлов к обработке: {len(selected_files)}")
        print("=" * 50)
        
        confirm = input("\nНачать обработку? [y/n]: ").strip().lower()
        if confirm not in ['y', 'yes', 'д', 'да']:
            continue
        
        # Обработка файлов
        print(f"\n" + "=" * 50)
        print("               ОБРАБОТКА")
        print("=" * 50)
        
        success_count = 0
        for epub_file in selected_files:
            try:
                process_epub(epub_file, modification_type, margin_size, output_mode, output_dir)
                success_count += 1
            except Exception as e:
                print(f"Ошибка: {epub_file} - {e}")
        
        print(f"\n" + "=" * 50)
        print(f"Обработано {success_count} из {len(selected_files)} файлов")
        
        if output_mode == "folder" and success_count > 0:
            print("Сохранено в папку 'books-upgrade'")
        
        print("=" * 50)
        
        # Спросить, хочет ли пользователь обработать еще файлы
        another = input("\nПродолжить работу? [y/n]: ").strip().lower()
        if another not in ['y', 'yes', 'д', 'да']:
            print("\nРабота завершена.")
            break

if __name__ == "__main__":
    main()