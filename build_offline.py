"""
Build Script для создания Offline Standalone версии Exam System
Использует PyInstaller для упаковки в EXE
"""

import os
import shutil
import subprocess
import sys

# Настройка кодировки для Windows консоли
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 60)
print("Exam System - Offline Standalone Builder")
print("=" * 60)
print()

# Шаг 1: Проверка зависимостей
print("1. Проверка зависимостей...")
try:
    import PyInstaller
    print("   ✓ PyInstaller установлен")
except ImportError:
    print("   ✗ PyInstaller не найден. Устанавливаем...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("   ✓ PyInstaller установлен")

# Шаг 2: Создание структуры
print("\n2. Подготовка структуры...")
dist_folder = "ExamSystem-Offline"
if os.path.exists(dist_folder):
    shutil.rmtree(dist_folder)
os.makedirs(dist_folder)
print(f"   ✓ Папка {dist_folder} создана")

# Шаг 3: Копирование необходимых файлов и папок
print("\n3. Копирование файлов...")

files_to_copy = [
    "app.py",
    "config.py",
    "consts.py",
    "Exam.py",
    "script.js",
    "requirements.txt",
    "README.md"
]

folders_to_copy = [
    "data",
    "templates",
    "static",
    "services",
    "routes",
    "video",
    "Exams"  # Папка с примерами экзаменов
]

for file in files_to_copy:
    if os.path.exists(file):
        shutil.copy2(file, os.path.join(dist_folder, file))
        print(f"   ✓ {file}")

for folder in folders_to_copy:
    if os.path.exists(folder):
        dest = os.path.join(dist_folder, folder)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(folder, dest)
        print(f"   ✓ {folder}/")

# Создаем пустые папки для результатов и логов
os.makedirs(os.path.join(dist_folder, "teachers"), exist_ok=True)
os.makedirs(os.path.join(dist_folder, "logs"), exist_ok=True)
print("   ✓ teachers/ (пустая)")
print("   ✓ logs/ (пустая)")

# Шаг 4: Создание EXE с PyInstaller
print("\n4. Создание EXE файла...")
print("   Это может занять несколько минут...")

# Используем готовый spec файл вместо создания команды вручную
pyinstaller_cmd = [
    "pyinstaller",
    "ExamSystem_Offline.spec",
    "--clean",
    "--noconfirm"
]

try:
    result = subprocess.run(pyinstaller_cmd, check=True, capture_output=True, text=True)
    print("   ✓ EXE файл создан")
except subprocess.CalledProcessError as e:
    print(f"   ✗ Ошибка при создании EXE:")
    print(e.stderr)
    sys.exit(1)

# Шаг 5: Копирование EXE в финальную папку
print("\n5. Сборка финального пакета...")
exe_file = os.path.join("dist", "ExamSystem", "ExamSystem.exe")
if os.path.exists(exe_file):
    shutil.copy2(exe_file, os.path.join(dist_folder, "ExamSystem.exe"))
    print("   ✓ ExamSystem.exe")
else:
    print("   ✗ EXE файл не найден!")
    sys.exit(1)

# Шаг 6: Создание README для пользователей
print("\n6. Создание инструкции...")
readme_content = """# Exam System - Offline Standalone

## 🚀 Быстрый старт

1. **Запустите** `ExamSystem.exe`
2. **Нажмите** "Запустить сервер"
3. **Скопируйте** URL (например: http://192.168.1.100:5001)
4. **Передайте** этот URL ученикам

## 📋 Инструкция

### Для учителя:

1. Скопируйте папку `ExamSystem-Offline` на компьютер
2. Запустите `ExamSystem.exe`
3. Нажмите "▶ Запустить сервер"
4. Браузер откроется автоматически
5. Войдите в систему (username: teacher1, password: password)

### Для учеников:

Ученики подключаются по IP адресу учительского компьютера:
- Откройте браузер
- Введите URL, который дал учитель (например: http://192.168.1.100:5001)
- Начните экзамен

## 📁 Структура папок

```
ExamSystem-Offline/
├── ExamSystem.exe        ← Запускать это!
├── Exams/                ← Файлы экзаменов (.txt)
├── teachers/             ← Папки учителей (создаются автоматически)
├── data/                 ← База данных
├── video/                ← Обучающие видео
├── templates/            ← HTML шаблоны
└── static/               ← CSS, JS, изображения
```

## ⚙️ Добавление экзаменов

1. Поместите файлы экзаменов (.txt) в папку `Exams/`
2. В системе: "Мои экзамены" → "Добавить экзамен"
3. Выберите файл из папки Exams/

## 🔒 Безопасность

- Все данные хранятся локально
- Работает без интернета
- Можно копировать на флешку

## ❓ Проблемы

### Сервер не запускается
- Проверьте, что порт 5001 свободен
- Закройте другие приложения
- Перезапустите ExamSystem.exe

### Ученики не могут подключиться
- Проверьте, что все в одной локальной сети
- Убедитесь, что firewall не блокирует порт 5001
- Попробуйте использовать IP адрес (не localhost)

## 📞 Поддержка

YaM SOFT © 2026
"""

with open(os.path.join(dist_folder, "ИНСТРУКЦИЯ.txt"), "w", encoding="utf-8") as f:
    f.write(readme_content)
print("   ✓ ИНСТРУКЦИЯ.txt")

# Шаг 7: Создание ZIP архива
print("\n7. Создание ZIP архива...")
try:
    shutil.make_archive(dist_folder, 'zip', dist_folder)
    print(f"   ✓ {dist_folder}.zip создан")
except Exception as e:
    print(f"   ⚠ Не удалось создать ZIP: {e}")

# Шаг 8: Очистка временных файлов
print("\n8. Очистка...")
if os.path.exists("build"):
    shutil.rmtree("build")
    print("   ✓ build/ удалена")
if os.path.exists("dist"):
    shutil.rmtree("dist")
    print("   ✓ dist/ удалена")
if os.path.exists("ExamSystem.spec"):
    os.remove("ExamSystem.spec")
    print("   ✓ ExamSystem.spec удален")

# Финал
print("\n" + "=" * 60)
print("✅ ГОТОВО!")
print("=" * 60)
print(f"\n📦 Результат: {dist_folder}/")
print(f"📦 Архив: {dist_folder}.zip")
print(f"\n💾 Размер папки: {sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, dirnames, filenames in os.walk(dist_folder) for filename in filenames) / 1024 / 1024:.1f} MB")
print("\n🚀 Готово к распространению!")
print("   • Скопируйте папку на флешку")
print("   • Или отправьте ZIP файл")
print("   • Работает на Windows 7/8/10/11")
print()
