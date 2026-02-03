# ИНСТРУКЦИЯ ПО ДОБАВЛЕНИЮ НОВОГО ЯЗЫКА

## Этапы добавления нового языка (например, испанский - ES)

### Шаг 1: Создать новый JSON файл переводов
**Файл:** `data/translations/es.json`

Скопировать структуру из одного из существующих файлов (en.json) и перевести ВСЕ значения.

**Структура:**
```json
{
    "_meta": {
        "language": "Español",
        "direction": "ltr"
    },
    
    // === COPY ALL KEYS FROM INDEX ===
    // Смотреть TRANSLATIONS_INDEX.md для всех ключей (ID 1.x, 20.x, 100.x и т.д.)
    
    "login": "Iniciar sesión",
    "password": "Contraseña",
    ...
}
```

### Шаг 2: Обновить app.py - функция загрузки переводов

**Файл:** `app.py`

Найти функцию загрузки переводов (примерно строка 350-400) и добавить 'es':

```python
SUPPORTED_LANGUAGES = ['en', 'ru', 'he', 'es']  # ← добавить 'es'

@app.route('/api/translations/<lang>')
def get_translations(lang):
    if lang not in SUPPORTED_LANGUAGES:  # Будет проверять 'es'
        lang = 'en'
    
    # Автоматически загружает translations/es.json
    filepath = os.path.join(app_config.DATA_DIR, 'translations', f'{lang}.json')
    ...
```

### Шаг 3: Обновить i18n.js - список поддерживаемых языков

**Файл:** `static/js/i18n.js`

Найти (примерно строка 11):
```javascript
this.supportedLanguages = ['en', 'ru', 'he', 'es'];  // ← добавить 'es'
```

### Шаг 4: Добавить кнопку в языковой селектор

**Файл:** `templates/base.html`

Найти (примерно строки 62-68):
```html
<div class="language-switcher">
    <button id="lang-en" class="active" data-i18n="english">English</button>
    <button id="lang-ru" data-i18n="russian">Русский</button>
    <button id="lang-he" data-i18n="hebrew">עברית</button>
    <!-- ↓ Добавить новую кнопку ↓ -->
    <button id="lang-es" data-i18n="spanish">Español</button>
</div>
```

### Шаг 5: Добавить обработчик для нового языка в JavaScript

**Файл:** `templates/base.html` (в блоке script, примерно строка 110-130)

Найти код обработчиков кнопок языков:
```javascript
document.getElementById('lang-en').addEventListener('click', async () => {
    await i18n.loadLanguage('en');
    location.reload();
});

// Добавить:
document.getElementById('lang-es').addEventListener('click', async () => {
    await i18n.loadLanguage('es');
    location.reload();
});
```

### Шаг 6: Добавить перевод названия языка в сами переводы

В файле **en.json** добавить:
```json
"spanish": "Español"
```

В файле **ru.json** добавить:
```json
"spanish": "Испанский"
```

В файле **he.json** добавить:
```json
"spanish": "ספרדית"
```

В файле **es.json** добавить:
```json
"spanish": "Español"
```

### Шаг 7: Обновить TRANSLATIONS_INDEX.md

Добавить новую запись в индекс:
```markdown
| 150.4 | `spanish` | Spanish | Испанский | ספרדית | base.html language selector |
```

### Шаг 8: Обновить detect_exam_language() в app.py (если нужно)

Если новый язык использует другой script/алфавит, добавить его определение:

```python
def detect_exam_language(content):
    hebrew_count = 0
    russian_count = 0
    spanish_count = 0  # ← новый счетчик (если нужен)
    
    for char in content:
        if "\u0590" <= char <= "\u05FF":
            hebrew_count += 1
        elif "\u0400" <= char <= "\u04FF":
            russian_count += 1
        # Испанский использует латиницу, поэтому отдельного детектора не нужно
    
    if hebrew_count > len(content) * 0.1:
        return 'he'
    elif russian_count > len(content) * 0.1:
        return 'ru'
    return 'en'  # Spanish будет работать как English (LTR)
```

### Шаг 9: Тестирование

1. Убедиться что файл `es.json` валиден (проверить JSON синтаксис)
2. Перезагрузить приложение
3. Проверить что кнопка "Español" появилась в селекторе
4. Клик по кнопке → проверить что язык изменился
5. Загрузить экзамен на испанском → проверить RTL если нужно (испанский LTR)

---

## ВАЖНЫЕ ЗАМЕЧАНИЯ

### RTL vs LTR
- **RTL (справа-налево):** иврит, арабский
  - Устанавливать `direction: "rtl"` в `_meta`
  - CSS автоматически применит правила из `rtl.css`
- **LTR (слева-направо):** английский, русский, испанский
  - Устанавливать `direction: "ltr"` в `_meta`

### Структура файлов
```
translations/
├── TRANSLATIONS_INDEX.md      ← Этот файл - главная справка
├── SCHEMA.js                  ← Описание структуры JSON
├── en.json                    ← Английский (LTR)
├── ru.json                    ← Русский (LTR)
├── he.json                    ← Иврит (RTL)
└── [es.json]                  ← НОВЫЙ язык (если добавляете)
```

### Повторное напоминание
**⚠️ НЕ ПОРТИТЬ СУЩЕСТВУЮЩИЕ СЛОВАРИ!**

- Не апендить к существующим ключам
- Не создавать дублирующиеся ключи
- Всегда проверять TRANSLATIONS_INDEX.md перед добавлением
- Если сомневаетесь - посмотреть как сделано для других языков

---

## Контрольный список

- [ ] Создан файл `es.json` со всеми ключами из индекса
- [ ] Обновлен `app.py` - добавлены 'es' в SUPPORTED_LANGUAGES
- [ ] Обновлен `i18n.js` - добавлены 'es' в supportedLanguages
- [ ] Добавлена кнопка в base.html language selector
- [ ] Добавлен обработчик клика в base.html script
- [ ] Добавлены переводы слова "spanish" во все JSON файлы
- [ ] Обновлен TRANSLATIONS_INDEX.md
- [ ] Протестировано переключение языка
- [ ] Протестирован экзамен на новом языке
- [ ] Проверена валидность всех JSON файлов

