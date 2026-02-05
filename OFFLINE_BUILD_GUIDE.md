# 📦 Полное руководство: Создание Offline Standalone версии

## 🎯 Цель
Создать автономную Windows версию системы экзаменов, которая работает без установки Python и интернета.

---

## 📋 Требования

### Необходимые инструменты:
- **Python 3.13.9** (или выше)
- **PyInstaller 6.18.0** (или выше)
- **PowerShell** для скриптов сборки

### Установка PyInstaller:
```powershell
pip install pyinstaller==6.18.0
```

---

## 🛠️ Процесс сборки (пошагово)

### 1. Подготовка файлов

#### Создать `launcher_offline.py`:
**Назначение:** Главный entry point для .exe, управляет сервером и браузером

**Ключевые особенности:**
- Использует `werkzeug.serving.make_server` вместо `app.run()`
- Signal handlers (SIGINT, SIGTERM) для graceful shutdown
- Запуск сервера в отдельном потоке (daemon thread)
- Автоматическое открытие браузера
- Определение BASE_DIR для frozen mode

```python
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
```

#### Создать `ExamSystem_Offline.spec`:
**Назначение:** Конфигурация PyInstaller для упаковки приложения

**Важные настройки:**
```python
# Сбор всех Flask зависимостей
for pkg in ['flask', 'werkzeug', 'jinja2', 'click', 'itsdangerous', 'markupsafe']:
    tmp_ret = collect_all(pkg)
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]

# Папки данных приложения
datas += [
    ('templates', 'templates'),
    ('static', 'static'),
    ('data', 'data'),           # Переводы
    ('services', 'services'),
    ('routes', 'routes'),
    ('video', 'video'),
    ('Exams', 'Exams'),         # Примеры экзаменов
]

# Скрытые импорты
hiddenimports += [
    'flask', 'werkzeug', 'jinja2',
    'werkzeug.security', 'werkzeug.serving',
    'werkzeug.middleware.proxy_fix',
    'sqlite3', 'hashlib', 'logging',
    # ... и другие
]
```

---

### 2. Исправление путей в config.py

**КРИТИЧЕСКИ ВАЖНО!** PyInstaller помещает файлы данных в `_internal/`, нужно это учитывать:

```python
class Config:
    # Database paths - FIXED for PyInstaller standalone mode
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        # PyInstaller extracts bundled files to _internal folder
        BUNDLE_DIR = os.path.join(os.path.dirname(sys.executable), '_internal')
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        # Running in development
        BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Read-only data (translations) from bundle, writable data (db, logs) from base
    DATA_DIR = os.path.join(BUNDLE_DIR, 'data')  # Для translations в _internal
    TEACHERS_DIR = os.path.join(BASE_DIR, 'teachers')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Database - must be writable, so store next to exe not in bundle
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'users.db')
```

**Почему это важно:**
- `_internal/data/translations/` - read-only файлы переводов (упакованы в exe)
- `data/users.db` - writable база данных (рядом с exe)
- `teachers/` - writable папка экзаменов (рядом с exe)

---

### 3. Исправление путей к примерам экзаменов (Exams/)

В `app.py` нужно проверять оба места:

```python
# В функциях get_examples_list(), copy_example(), get_exam_source_from_examples()
# Check BASE_DIR first, then BUNDLE_DIR (for PyInstaller)
examples_dir = os.path.join(app_config.BASE_DIR, 'Exams')
if not os.path.exists(examples_dir) and hasattr(app_config, 'BUNDLE_DIR'):
    examples_dir = os.path.join(app_config.BUNDLE_DIR, 'Exams')
```

**Логика:**
- Сначала проверяем `Exams/` рядом с exe (если пользователь добавил свои)
- Если нет - используем `_internal/Exams/` (упакованные примеры)

---

### 4. Исправление схемы базы данных

**ВАЖНО!** Схема БД должна совпадать с `auth_service.py`:

```python
# В setup_offline_db.py
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        first_name TEXT NOT NULL,      # ← ОБЯЗАТЕЛЬНО
        last_name TEXT NOT NULL,        # ← ОБЯЗАТЕЛЬНО
        email TEXT,                     # ← ОБЯЗАТЕЛЬНО
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        terms_accepted_at TIMESTAMP
    )
''')
```

**Ошибка без этого:**
```
Authentication error: no such column: first_name
```

---

### 5. Сборка executable

#### Метод 1: Прямой запуск PyInstaller
```powershell
python -m PyInstaller ExamSystem_Offline.spec --noconfirm --clean
```

#### Метод 2: Использовать скрипт (рекомендуется)
```powershell
.\build_simple.ps1
```

**Опции:**
- `--noconfirm` - перезаписать без подтверждения
- `--clean` - очистить кэш перед сборкой (полезно при проблемах)

**Время сборки:** ~1-2 минуты

**Результат:** `dist\ExamSystem\ExamSystem.exe` (~5.4 MB)

---

### 6. Создание базы данных с тестовым пользователем

После сборки **ОБЯЗАТЕЛЬНО** создать БД с правильной схемой:

```powershell
python setup_offline_db.py
```

Это создаст:
- `dist\ExamSystem\data\users.db` с правильной схемой
- Тестового пользователя: `teacher` / `teacher123`

---

### 7. Копирование примеров экзаменов (опционально)

Если хотите примеры рядом с exe (а не в _internal):

```powershell
Copy-Item "Exams\*.txt" "dist\ExamSystem\Exams\" -Force
```

---

## 📂 Структура готовой сборки

```
dist/ExamSystem/
├── ExamSystem.exe              # Главный исполняемый файл
├── python313.dll               # Python runtime
├── data/                       # Записываемые данные
│   └── users.db               # База данных
├── teachers/                  # Папки преподавателей (создаются автоматически)
├── logs/                      # Логи сервера
├── Exams/                     # Дополнительные примеры (опционально)
└── _internal/                 # Внутренние файлы PyInstaller (READ-ONLY)
    ├── base_library.zip       # Python stdlib
    ├── data/
    │   └── translations/      # Файлы переводов (en/ru/he)
    │       ├── en.json
    │       ├── he.json
    │       └── ru.json
    ├── Exams/                 # Примеры экзаменов (упакованные)
    ├── templates/             # HTML шаблоны
    ├── static/                # CSS/JS файлы
    ├── services/              # Python сервисы
    ├── routes/                # Flask routes
    ├── video/                 # Видео файлы
    └── [множество .pyd/.dll]  # Python библиотеки
```

---

## 🐛 Известные проблемы и решения

### Проблема 1: Ошибка 500 при загрузке переводов
**Симптом:**
```
api/translations/he:1  Failed to load resource: the server responded with a status of 500
```

**Причина:** config.py ищет translations в неправильном месте

**Решение:** Используйте `BUNDLE_DIR` для read-only данных (см. раздел 2)

---

### Проблема 2: "no such column: first_name"
**Симптом:**
```
Authentication error: no such column: first_name
```

**Причина:** База данных создана с упрощённой схемой

**Решение:** 
1. Удалить `dist\ExamSystem\data\users.db`
2. Запустить `python setup_offline_db.py`

---

### Проблема 3: Примеры экзаменов не загружаются
**Симптом:** Кнопка "Load from Examples" показывает пустой список

**Причина:** Папка `Exams/` не найдена

**Решение:**
1. Скопировать примеры: `Copy-Item "Exams\*.txt" "dist\ExamSystem\Exams\"`
2. Или исправить код для проверки `BUNDLE_DIR/Exams` (см. раздел 3)

---

### Проблема 4: Файлы заблокированы при пересборке
**Симптом:**
```
PermissionError: [WinError 5] Access is denied: 'dist\ExamSystem\_internal\...'
```

**Решение:**
```powershell
# Остановить процесс
Get-Process ExamSystem -ErrorAction SilentlyContinue | Stop-Process -Force

# Удалить dist
Remove-Item -Recurse -Force "dist", "build"

# Пересобрать
python -m PyInstaller ExamSystem_Offline.spec --noconfirm --clean
```

---

### Проблема 5: Сервер не закрывается gracefully
**Симптом:** При нажатии Ctrl+C сервер падает с ошибкой

**Решение:** Используйте signal handlers в launcher_offline.py:
```python
def signal_handler(sig, frame):
    if server:
        server.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

---

## ✅ Чеклист перед релизом

- [ ] Запустить `ExamSystem.exe`
- [ ] Проверить автоматическое открытие браузера
- [ ] Проверить логин (teacher / teacher123)
- [ ] Проверить переключение языков (EN/RU/HE)
- [ ] Проверить загрузку примеров экзаменов
- [ ] Проверить создание нового экзамена
- [ ] Проверить загрузку экзамена из файла
- [ ] Проверить graceful shutdown (Ctrl+C)
- [ ] Проверить размер exe (~5-6 MB нормально)
- [ ] Проверить отсутствие ошибок в console

---

## 📦 Создание дистрибутива (ZIP)

```powershell
# Создать ZIP для распространения
Compress-Archive -Path "dist\ExamSystem\*" -DestinationPath "ExamSystem-Offline-v1.0.zip" -Force
```

**Что включить:**
- `ExamSystem.exe` + все файлы из `dist\ExamSystem\`
- `README.txt` с инструкциями для пользователя
- Примеры экзаменов (уже внутри)

---

## 🔄 Процесс обновления при изменениях в коде

### Если изменили Python код (app.py, services/, и т.д.):
```powershell
# 1. Остановить ExamSystem
Get-Process ExamSystem -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Очистить старую сборку
Remove-Item -Recurse -Force "dist", "build"

# 3. Пересобрать
python -m PyInstaller ExamSystem_Offline.spec --noconfirm --clean

# 4. База данных останется (не пересоздавать!)
# Только если нужна новая схема БД - тогда:
# python setup_offline_db.py
```

### Если изменили только статику (HTML/CSS/JS):
```powershell
# Быстрая пересборка (без --clean)
python -m PyInstaller ExamSystem_Offline.spec --noconfirm
```

### Если изменили переводы (data/translations/*.json):
```powershell
# Переводы упакованы в exe, нужна пересборка
python -m PyInstaller ExamSystem_Offline.spec --noconfirm
```

---

## 📝 Важные файлы для offline версии

### Обязательные:
- ✅ `launcher_offline.py` - Entry point
- ✅ `ExamSystem_Offline.spec` - Конфигурация PyInstaller
- ✅ `config.py` - Пути с поддержкой frozen mode
- ✅ `setup_offline_db.py` - Создание БД
- ✅ `app.py` - Flask приложение (с исправленными путями к Exams)

### Опциональные:
- `build_simple.ps1` - Автоматизация сборки
- `OFFLINE_BUILD_GUIDE.md` - Это руководство

---

## 🎓 Советы и best practices

### 1. Тестирование перед релизом
Всегда тестируйте на **чистой системе** без Python:
- Удалите все переменные окружения Python
- Запустите exe в папке без Python

### 2. Размер exe
Нормальный размер: **5-6 MB**  
Если больше 10 MB - проверьте excludes в .spec файле

### 3. Безопасность
- Не храните пароли в коде
- Используйте SESSION_COOKIE_SECURE=False только для offline
- Для production версии (онлайн) используйте HTTPS

### 4. Логирование
Логи сохраняются в `logs/` - помогает при отладке

### 5. База данных
SQLite с WAL mode для лучшей concurrent производительности

---

## 🌐 Различия online vs offline версий

| Параметр | Online (main branch) | Offline (offline-standalone) |
|----------|---------------------|----------------------------|
| **Запуск** | `python app.py` | `ExamSystem.exe` |
| **Python** | Требуется | Не требуется (встроен) |
| **База** | PostgreSQL/MySQL | SQLite |
| **HTTPS** | Обязательно | HTTP (localhost) |
| **Портативность** | Нет | Полная |
| **Размер** | ~10-20MB (код) | ~5.4MB (exe+данные) |
| **Обновление** | Git pull | Новый exe файл |

---

## ❓ FAQ

**Q: Можно ли использовать offline версию в сети?**  
A: Да! Запустите на одном компьютере, другие подключаются по IP:5000

**Q: Как изменить порт?**  
A: В `launcher_offline.py` измените `port = 5000`

**Q: Почему exe такой большой?**  
A: Включает Python runtime + Flask + все зависимости

**Q: Можно ли добавить свои экзамены?**  
A: Да! Положите .txt файлы в `Exams/` рядом с exe

**Q: Работает ли на Linux/Mac?**  
A: Эта сборка для Windows. Для Linux/Mac нужна отдельная сборка.

---

## 📞 Поддержка

При проблемах проверьте:
1. Логи в `logs/`
2. Console output (окно с ExamSystem.exe)
3. Browser console (F12)

---

**Версия руководства:** 1.0  
**Дата:** 5 февраля 2026  
**Ветка:** offline-standalone  
**Совместимость:** Windows 10/11, Python 3.13.9, PyInstaller 6.18.0
