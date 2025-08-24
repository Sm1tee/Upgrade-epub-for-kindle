# EPUB Margin Reducer for Kindle

Простой и эффективный скрипт для уменьшения полей в EPUB книгах, специально оптимизированный для устройств Kindle.

## 🎯 Проблема

Kindle имеет встроенные ограничения на минимальный размер полей, которые нельзя уменьшить через настройки устройства. Это приводит к тому, что на экране отображается меньше текста, особенно заметно на компактных моделях Kindle.

## ✨ Решение

Скрипт автоматически модифицирует CSS стили в EPUB файлах, добавляя отрицательные отступы, которые эффективно расширяют текстовую область за счет полей.

## 🚀 Возможности

- ✅ **Безопасная обработка** - оригинальные файлы остаются нетронутыми
- ✅ **Пакетная обработка** - можно обработать все книги в папке одной командой
- ✅ **Настраиваемые поля** - можно изменить размер отступов (по умолчанию -20px)
- ✅ **Умные фильтры** - автоматически пропускает уже обработанные файлы
- ✅ **Поддержка масок** - обработка файлов по шаблону (например, `*.epub`)
- ✅ **Кроссплатформенность** - работает на Windows, macOS, Linux

## 📋 Требования

- Python 3.6 или выше
- Стандартные библиотеки Python (zipfile, tempfile, pathlib)


## 🔧 Быстрый старт

### Пошаговая инструкция для новичков

1. **Скачайте скрипт** `modify_epub_margins.py`
2. **Поместите его в папку с книгами** (например, `C:\Books\` или `~/Downloads/Books/`)
3. **Откройте командную строку в этой папке:**
   - Windows: Shift + правый клик → "Открыть окно PowerShell здесь"
   - Linux: правый клик → "Открыть терминал здесь"
4. **Запустите команду:**
   - Windows: `python modify_epub_margins.py`
   - Linux: `python3 modify_epub_margins.py`

Готово! Все .epub файлы в папке будут обработаны.

## 🔧 Использование

### Windows (cmd/PowerShell)
```cmd
# Обработать все .epub файлы в текущей папке
python modify_epub_margins.py

# Обработать конкретный файл
python modify_epub_margins.py "Моя книга.epub"

# Изменить размер отступов (будет -30px)
python modify_epub_margins.py --margin 30

# Обработать файлы с кастомными отступами (будет -15px)
python modify_epub_margins.py --margin 15 *.epub

# Показать справку
python modify_epub_margins.py --help
```

### Linux/macOS (bash)
```bash
# Обработать все .epub файлы в текущей папке
python3 modify_epub_margins.py

# То же самое, но явно
python3 modify_epub_margins.py --all

# Обработать конкретный файл
python3 modify_epub_margins.py "Моя книга.epub"

# Изменить размер отступов (будет -25px)
python3 modify_epub_margins.py --margin 25

# Обработать несколько файлов с кастомными отступами (будет -15px)
python3 modify_epub_margins.py --margin 15 book1.epub book2.epub

# Использовать маски
python3 modify_epub_margins.py "Гарри Поттер"*.epub
```

### Примеры использования

**Скрипт в папке с книгами (рекомендуется):**
```cmd
# Windows - все книги в текущей папке
python modify_epub_margins.py

# Linux - все книги в текущей папке  
python3 modify_epub_margins.py
```

**Скрипт в отдельной папке - указываем полные пути:**
```cmd
# Windows - полный путь к книге
python modify_epub_margins.py "C:\Users\Username\Downloads\Books\Моя книга.epub"

# Windows - полный путь к папке с книгами
python modify_epub_margins.py "C:\Users\Username\Downloads\Books\*.epub"
```

```bash
# Linux - полный путь к книге
python3 modify_epub_margins.py "/home/user/Downloads/Books/Моя книга.epub"

# Linux - все книги в указанной папке
python3 modify_epub_margins.py /home/user/Downloads/Books/*.epub
```

**Обработка с кастомными отступами:**
```bash
# Малые отступы (-10px) для больших экранов
python3 modify_epub_margins.py --margin 10 *.epub

# Большие отступы (-30px) для маленьких экранов
python3 modify_epub_margins.py --margin 30 "Война и мир.epub"
```

## 📁 Структура выходных файлов

Скрипт создает новые файлы с суффиксом `-upgrade`:

```
Исходный файл:    Война и мир.epub
Результат:        Война и мир-upgrade.epub
```

Оригинальные файлы остаются нетронутыми.

## ⚙️ Технические детали

### Что делает скрипт

1. **Распаковывает** EPUB файл во временную директорию
2. **Находит** основной CSS файл (обычно `OPS/style.css` или `OEBPS/style.css`)
3. **Добавляет** CSS правила для уменьшения полей (по умолчанию -20px):
   ```css
   html, body {
       margin-left: -20px !important;
       margin-right: -20px !important;
       padding: 0 !important;
   }
   ```
4. **Упаковывает** файлы обратно в валидный EPUB
5. **Очищает** временные файлы


### Поддерживаемые структуры EPUB

Скрипт автоматически определяет расположение CSS файлов:
- `OPS/style.css` (стандарт)
- `OEBPS/style.css` (альтернативный стандарт)
- `styles/style.css` (некоторые конвертеры)
- `css/style.css` (редкие случаи)

Если CSS файл не найден, скрипт создает новый.

---

**Наслаждайтесь чтением с максимальным использованием экрана! 📚✨**
