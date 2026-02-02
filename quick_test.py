#!/usr/bin/env python3
"""
Quick Test - Проверка всех компонентов приложения
"""

import os
import sys
import json

def check_files():
    """Проверить наличие всех необходимых файлов"""
    print("📋 Проверка файлов...")
    
    required_files = {
        'app.py': 'Flask приложение',
        'config.py': 'Конфигурация',
        'requirements.txt': 'Зависимости',
        'static/css/base.css': 'Base CSS',
        'static/css/responsive.css': 'Responsive CSS',
        'static/css/rtl.css': 'RTL CSS',
        'static/js/i18n.js': 'i18n система',
        'static/js/exam_script.js': 'Логика экзамена',
        'templates/login.html': 'Шаблон логина',
        'templates/exam.html': 'Шаблон экзамена',
        'templates/teacher_dashboard.html': 'Панель учителя',
        'data/translations/en.json': 'English переводы',
        'data/translations/ru.json': 'Russian переводы',
        'data/translations/he.json': 'Hebrew переводы',
        'services/auth_service.py': 'Аутентификация',
        'services/exam_service.py': 'Экзамены',
        'services/proctoring_service.py': 'Прокторинг',
        'services/file_service.py': 'Работа с файлами',
    }
    
    missing = []
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✓ {file_path:<40} ({size:>6} bytes) - {description}")
        else:
            print(f"  ✗ {file_path:<40} - ОТСУТСТВУЕТ!")
            missing.append(file_path)
    
    return len(missing) == 0


def check_directories():
    """Проверить наличие необходимых директорий"""
    print("\n📁 Проверка директорий...")
    
    required_dirs = {
        'static': 'Статические файлы',
        'templates': 'Шаблоны',
        'services': 'Сервисы',
        'data': 'Данные',
        'data/translations': 'Переводы',
        'logs': 'Логи',
        'teachers': 'Папки учителей',
    }
    
    missing = []
    for dir_path, description in required_dirs.items():
        if os.path.isdir(dir_path):
            print(f"  ✓ {dir_path:<40} - {description}")
        else:
            print(f"  ✗ {dir_path:<40} - ОТСУТСТВУЕТ!")
            missing.append(dir_path)
    
    return len(missing) == 0


def check_imports():
    """Проверить импорты Python модулей"""
    print("\n🐍 Проверка Python импортов...")
    
    modules = {
        'flask': 'Flask',
        'werkzeug': 'Werkzeug',
        'json': 'JSON',
        'sqlite3': 'SQLite3',
        'hashlib': 'HashLib',
        'os': 'OS',
    }
    
    missing = []
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"  ✓ {module:<20} - {description}")
        except ImportError:
            print(f"  ✗ {module:<20} - ОТСУТСТВУЕТ!")
            missing.append(module)
    
    return len(missing) == 0


def check_translations():
    """Проверить наличие переводов"""
    print("\n🌍 Проверка переводов...")
    
    languages = {
        'en': 'English',
        'ru': 'Russian',
        'he': 'Hebrew',
    }
    
    missing = []
    for lang_code, lang_name in languages.items():
        path = f'data/translations/{lang_code}.json'
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                keys = len(data)
                print(f"  ✓ {lang_code:<5} - {lang_name:<15} ({keys} ключей)")
        except Exception as e:
            print(f"  ✗ {lang_code:<5} - ОШИБКА: {e}")
            missing.append(lang_code)
    
    return len(missing) == 0


def check_app_import():
    """Проверить что Flask приложение импортируется"""
    print("\n🚀 Проверка Flask приложения...")
    
    try:
        from app import app, auth_service
        print(f"  ✓ Flask приложение импортировано успешно")
        print(f"  ✓ auth_service готов к использованию")
        
        # Проверить БД
        user = auth_service.get_user(1)
        if user:
            print(f"  ✓ Тестовый пользователь найден: {user['first_name']} {user['last_name']}")
        else:
            print(f"  ℹ БД пуста (создается при первом запуске)")
        
        return True
    except Exception as e:
        print(f"  ✗ ОШИБКА при импорте: {e}")
        return False


def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("🧪 QUICK TEST - Проверка компонентов приложения")
    print("="*60 + "\n")
    
    results = []
    
    # Проверки
    results.append(("Файлы", check_files()))
    results.append(("Директории", check_directories()))
    results.append(("Переводы", check_translations()))
    results.append(("Python модули", check_imports()))
    results.append(("Flask приложение", check_app_import()))
    
    # Итоги
    print("\n" + "="*60)
    print("📊 ИТОГИ")
    print("="*60)
    
    for check_name, result in results:
        status = "✓ OK" if result else "✗ ОШИБКА"
        print(f"  {check_name:<30} {status}")
    
    all_passed = all(result for _, result in results)
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Приложение готово к запуску.\n")
        print("Запустите приложение:\n")
        print("  python app.py\n")
        print("Затем откройте в браузере:")
        print("  http://localhost:5000\n")
        print("Логин (по умолчанию):")
        print("  Username: teacher1")
        print("  Password: password123\n")
        return 0
    else:
        print("\n⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ! Решите их перед запуском.\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
