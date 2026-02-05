# 📦 Исправление Offline Version - Translations Fix

## ✅ Что было исправлено

### Проблема
При запуске standalone версии (ExamSystem.exe) возникала ошибка:
```
api/translations/he:1  Failed to load resource: the server responded with a status of 500 (INTERNAL SERVER ERROR)
```

### Причина
PyInstaller помещает файлы данных (data/) в папку `_internal`, но config.py искал их рядом с exe файлом.

### Решение
Исправлен **config.py** для работы с PyInstaller:
- Добавлена переменная `BUNDLE_DIR` для read-only файлов (находятся в `_internal/`)
- Переводы (translations) загружаются из `_internal/data/translations/`
- База данных (users.db) остаётся записываемой рядом с exe
- Logs и teachers папки создаются рядом с exe

## 📂 Структура
```
dist/ExamSystem/
├── ExamSystem.exe          # Главный исполняемый файл
├── data/                   # Записываемые данные
│   └── users.db           # База данных пользователей
├── teachers/              # Папки преподавателей
├── logs/                  # Логи сервера
└── _internal/             # Внутренние файлы PyInstaller (READ-ONLY)
    ├── data/
    │   └── translations/  # ✅ Файлы переводов (en/ru/he)
    │       ├── en.json
    │       ├── he.json
    │       └── ru.json
    ├── templates/         # HTML шаблоны
    ├── static/            # CSS/JS файлы
    └── ... (Python библиотеки)
```

## 🚀 Как запустить

1. **Двойной клик** на `ExamSystem.exe`
2. Браузер откроется автоматически
3. Логин: `teacher` / Пароль: `teacher123`

## 🔧 Технические детали

### Изменённые файлы:
1. **config.py** - добавлено разделение путей для frozen mode
2. **app.py** - обновлена функция ensure_directories()

### Изменения в config.py:
```python
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    # PyInstaller extracts bundled files to _internal folder
    BUNDLE_DIR = os.path.join(os.path.dirname(sys.executable), '_internal')
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running in development
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Read-only data from bundle, writable data from base
DATA_DIR = os.path.join(BUNDLE_DIR, 'data')  # Для translations
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'users.db')  # Для DB
```

## ✨ Результат
- ✅ Переводы загружаются правильно
- ✅ База данных работает
- ✅ Логин функционирует
- ✅ Сервер запускается без ошибок

## 📊 Сборка
- **Версия:** 19:56 (Feb 5, 2026)
- **Размер:** 5.41 MB
- **Python:** 3.13.9
- **PyInstaller:** 6.18.0

---
**Дата исправления:** 5 февраля 2026, 19:56
