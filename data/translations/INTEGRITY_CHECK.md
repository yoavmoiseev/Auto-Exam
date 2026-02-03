# INTEGRITY CHECK - Проверка целостности словарей

**Дата проверки:** 2026-02-03  
**Версия система:** 1.0

## Быстрая проверка (Quick Check)

Запусти это в Python консоли:

```python
import json
import os

translations_dir = 'data/translations'
languages = ['en', 'ru', 'he']

# 1. Проверка валидности JSON
print("=== JSON Validation ===")
for lang in languages:
    filepath = os.path.join(translations_dir, f'{lang}.json')
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✓ {lang}.json - OK")
    except json.JSONDecodeError as e:
        print(f"✗ {lang}.json - ERROR: {e}")

# 2. Проверка что все ключи совпадают
print("\n=== Key Consistency ===")
keys_dict = {}
for lang in languages:
    filepath = os.path.join(translations_dir, f'{lang}.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    keys_dict[lang] = set(data.keys())

# Находим различия
all_keys = set().union(*keys_dict.values())
for lang in languages:
    missing = all_keys - keys_dict[lang]
    extra = keys_dict[lang] - (all_keys - missing)
    if missing:
        print(f"✗ {lang}.json - Missing keys: {missing}")
    else:
        print(f"✓ {lang}.json - All {len(keys_dict[lang])} keys present")

# 3. Проверка критичных ключей
print("\n=== Critical Keys Check ===")
critical_keys = [
    'exam_name',
    'question_number', 
    'of',
    'previous',
    'next',
    'submit_exam',
    'company_name'
]

for lang in languages:
    filepath = os.path.join(translations_dir, f'{lang}.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    missing_critical = [k for k in critical_keys if k not in data]
    if missing_critical:
        print(f"✗ {lang}.json - Missing critical: {missing_critical}")
    else:
        print(f"✓ {lang}.json - All critical keys OK")

print("\n=== Check Complete ===")
```

## Детальная проверка (Full Audit)

### 1. Валидность JSON синтаксиса

```bash
# Windows PowerShell
python -m json.tool data/translations/en.json > $null
python -m json.tool data/translations/ru.json > $null
python -m json.tool data/translations/he.json > $null
```

Должно вывести без ошибок ✓

### 2. Проверка метаданных

Каждый файл должен иметь:
```json
{
    "_meta": {
        "language": "English" или "Русский" или "עברית",
        "direction": "ltr" или "rtl"
    },
    ...
}
```

**Проверить:**
- [ ] `en.json`: direction = "ltr"
- [ ] `ru.json`: direction = "ltr"
- [ ] `he.json`: direction = "rtl"

### 3. Количество ключей

**Ожидаемое:**
- `en.json`: ≥ 220 ключей (вкл. метаданные)
- `ru.json`: ≥ 220 ключей
- `he.json`: ≥ 220 ключей

**Проверить:**
```python
import json
for lang in ['en', 'ru', 'he']:
    with open(f'data/translations/{lang}.json') as f:
        data = json.load(f)
    print(f"{lang}.json: {len(data)} keys")
```

### 4. Критичные ключи (MUST HAVE)

Эти ключи **обязательны** для работы экзамена:

| ID | Ключ | Где используется |
|---|---|---|
| 100.1 | `exam_name` | exam.html |
| 100.2 | `question_number` | exam_script.js:282 |
| 100.3 | `of` | exam_script.js:282 |
| 100.4 | `previous` | exam.html + JS |
| 100.5 | `next` | exam.html + JS |
| 100.6 | `submit_exam` | exam.html |
| 100.7 | `start_exam` | exam.html |
| 150.1 | `english` | base.html |
| 150.2 | `russian` | base.html |
| 150.3 | `hebrew` | base.html |
| 1.4 | `company_name` | footer |

**Проверить что все эти ключи есть во всех трех файлах**

### 5. Отсутствие дублей

JSON ключи должны быть уникальны. Проверить что нет такого:

```json
{
    "previous": "Previous",
    ...
    "previous": "← Previous"   // ✗ ОШИБКА!
}
```

**Проверить:**
```python
import json
for lang in ['en', 'ru', 'he']:
    with open(f'data/translations/{lang}.json') as f:
        raw_text = f.read()
    # Простой поиск на наличие повторений
    lines = raw_text.split('\n')
    keys_seen = set()
    for line in lines:
        if ':' in line and '"' in line:
            key = line.split(':')[0].strip().strip('"')
            if key in keys_seen and key != '_meta':
                print(f"WARNING: {lang}.json has duplicate key: {key}")
            keys_seen.add(key)
```

### 6. Проверка RTL

Для иврита:
- [ ] `he.json` содержит `"direction": "rtl"`
- [ ] CSS файл `rtl.css` существует и применяется
- [ ] Тестирование в браузере показывает RTL расположение

### 7. Проверка использования в коде

Для каждого ключа должна быть ремарка где он используется:

```bash
# Поиск всех data-i18n атрибутов в HTML
grep -r "data-i18n" templates/

# Поиск всех i18n.t() вызовов в JS
grep -r "i18n\.t(" static/js/

# Результат должен совпадать с TRANSLATIONS_INDEX.md
```

### 8. Версионирование

Проверить CHANGELOG.md:
- [ ] Есть запись о текущей версии (1.0)?
- [ ] Описаны все добавленные ключи?
- [ ] Указана дата обновления?

### 9. Документация

Проверить наличие файлов:
- [ ] `README.md` - основная документация
- [ ] `TRANSLATIONS_INDEX.md` - полный индекс ключей
- [ ] `SCHEMA.js` - описание структуры
- [ ] `CHANGELOG.md` - история изменений
- [ ] `ADD_NEW_LANGUAGE.md` - инструкция расширения

### 10. Код разработчика

Проверить что все hardcoded тексты заменены на i18n:

```bash
# Поиск английских слов в шаблонах
grep -E "(Next|Previous|Question|Submit)" templates/exam.html

# Результат: должны быть только в data-i18n атрибутах, не в контенте!
```

## Контрольный список перед деплоем

- [ ] Все JSON файлы валидны (json.tool без ошибок)
- [ ] Все три файла содержат одинаковые ключи
- [ ] Нет дублирующихся ключей
- [ ] Все критичные ключи (ID 100.1-100.10) присутствуют
- [ ] RTL правильно настроен для иврита
- [ ] Нет повторений в JSON (одинаковые ключи)
- [ ] TRANSLATIONS_INDEX.md обновлен
- [ ] CHANGELOG.md обновлен
- [ ] Тестирование на всех трех языках прошло успешно
- [ ] Проверен RTL на мобильном устройстве

## Восстановление после ошибки

Если словарь испорчен:

1. **Найти ошибку**
   ```bash
   python -m json.tool data/translations/en.json 2>&1 | head -20
   ```

2. **Отверуть к последней версии из git**
   ```bash
   git checkout data/translations/en.json
   ```

3. **Или восстановить вручную из TRANSLATIONS_INDEX.md**
   - Найти испорченный ключ в индексе
   - Восстановить значение из описания
   - Проверить что восстановлено во всех трех файлах

## Логирование изменений

Каждое изменение должно быть задокументировано:

1. В `TRANSLATIONS_INDEX.md` - добавить примечание
2. В `CHANGELOG.md` - описать что изменилось
3. В код - добавить комментарий с ID ключа

Пример:
```javascript
// TRANSLATION TRACKING: ID 100.2 (question_number) + ID 100.3 (of)
// Используется для отображения "Question 1 of 10"
${i18n.t('question_number')} ${question.number} ${i18n.t('of')} ${this.questions.length}
```

---

**Помни:** Лучше потратить 5 минут на проверку теперь, чем 1 час на отладку потом! 🔍

