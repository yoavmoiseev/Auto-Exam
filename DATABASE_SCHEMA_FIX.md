# 🔧 Database Schema Fix

## ❌ Проблема
```
Authentication error: no such column: first_name
```

## 🔍 Причина
База данных была создана с упрощённой схемой (только `username`, `password`, `role`), но `auth_service.py` ожидает полную схему с колонками:
- `first_name`
- `last_name`  
- `email`
- `created_at`
- `last_login`
- `terms_accepted_at`

## ✅ Решение
Обновлён **setup_offline_db.py** для создания БД с правильной схемой:

```python
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,      # ← ДОБАВЛЕНО
    last_name TEXT NOT NULL,        # ← ДОБАВЛЕНО
    email TEXT,                     # ← ДОБАВЛЕНО
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    terms_accepted_at TIMESTAMP
)
```

## 🚀 Применено
1. ✅ Удалена старая БД с неправильной схемой
2. ✅ Создана новая БД с полной схемой
3. ✅ Создан тестовый пользователь:
   - Username: `teacher`
   - Password: `teacher123`
   - Name: `Test Teacher`
   - Email: `teacher@example.com`

## ✅ Результат
Логин теперь работает без ошибок!

---
**Дата:** 5 февраля 2026, 20:05
