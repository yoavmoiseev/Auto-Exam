# 🔧 ИСПРАВЛЕНИЯ ЛОГИНА - ИНСТРУКЦИЯ ПО ПЕРЕСБОРКЕ

## 📋 Что было исправлено:

### 1. ✅ Config.py - Правильные пути для standalone режима
**Проблема:** `BASE_DIR` определялся неправильно в .exe  
**Исправление:** Добавлена проверка `sys.frozen` для правильного определения базовой директории

```python
if getattr(sys, 'frozen', False):
    # Running as compiled exe - base dir is where exe is located
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running in development - base dir is script directory  
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
```

### 2. ✅ Session Cookie - Отключен HTTPS для offline режима
**Проблема:** `SESSION_COOKIE_SECURE = True` требует HTTPS  
**Исправление:** `SESSION_COOKIE_SECURE = False` для локальной работы

### 3. ✅ Autocomplete атрибуты в формах
**Проблема:** Browser warning про missing autocomplete  
**Исправление:** Добавлены правильные атрибуты:
- login.html: `autocomplete="username"` и `autocomplete="current-password"`
- signup.html: `autocomplete="new-password"` для новых паролей

## 🚀 КАК ПЕРЕСОБРАТЬ:

### Шаг 1: Закрыть все процессы ExamSystem

**Option A - Через Task Manager:**
1. Ctrl+Shift+Esc
2. Найти ExamSystem.exe
3. End Task

**Option B - PowerShell:**
```powershell
Get-Process | Where-Object { $_.ProcessName -like "*ExamSystem*" } | Stop-Process -Force
```

### Шаг 2: Закрыть Explorer window с dist\ExamSystem

Если Explorer держит папку открытой - закрой окно!

### Шаг 3: Пересобрать

```powershell
cd c:\Users\moise\OneDrive\Desktop\Ex
python -m PyInstaller ExamSystem_Offline.spec --noconfirm
```

Ждать 3-5 минут до завершения.

### Шаг 4: Проверить результат

```powershell
cd dist\ExamSystem
.\ExamSystem.exe
```

## 🎯 Что должно работать после пересборки:

✅ **База данных создается правильно** - в `dist\ExamSystem\data\users.db`  
✅ **Login работает** - пути к БД правильные  
✅ **Session cookies работают** - нет требования HTTPS  
✅ **Нет browser warnings** - autocomplete на месте  

## 🔑 Тестовый пользователь:

**Username:** `teacher`  
**Password:** `teacher123`

Этот пользователь уже существует в development БД. После первого запуска standalone версии:

1. **Option A:** Зарегистрируй нового пользователя через форму signup
2. **Option B:** Скопируй существующую БД:
   ```powershell
   copy data\users.db dist\ExamSystem\data\users.db
   ```

## ❗ ВАЖНО:

**Если сборка не может удалить dist:**

1. Закрой все:
   - ExamSystem.exe
   - Explorer с dist\ExamSystem
   - VSCode если открыт файл из dist
   
2. Или собери в другую папку:
   ```powershell
   # Временно переименуй dist
   Rename-Item dist dist_old -Force
   
   # Собери заново
   python -m PyInstaller ExamSystem_Offline.spec --noconfirm
   
   # После успеха удали старую
   Remove-Item dist_old -Recurse -Force
   ```

## 🧪 ТЕСТ ЛОГИНА:

После пересборки:

1. Запусти `dist\ExamSystem\ExamSystem.exe`
2. Открой инструменты разработчика (F12)
3. Перейди на страницу login
4. **Не должно быть предупреждений** про autocomplete
5. Введи username/password
6. **Login должен работать!**

## 📝 Изменённые файлы:

- ✅ `config.py` (BASE_DIR + SESSION_COOKIE_SECURE)
- ✅ `templates/login.html` (autocomplete attributes)
- ✅ `templates/signup.html` (autocomplete attributes)
- ✅ `create_test_user.py` (новый - для создания тестового юзера)

## 🐛 Если логин все равно не работает:

### Проверь пути в консоли при запуске:

```powershell
cd dist\ExamSystem
.\ExamSystem.exe
```

Консоль должна показать:
- `Server IP: ...`
- `Port: 5000`
- `URL: http://...`

### Проверь что БД создалась:

```powershell
Test-Path dist\ExamSystem\data\users.db
```

Должно вернуть `True`

### Проверь логи если есть:

```powershell
Get-Content dist\ExamSystem\logs\*.log -Tail 50
```

---

**После пересборки всё должно работать!** 🎉
