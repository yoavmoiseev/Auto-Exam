# TRANSLATIONS INDEX - Полная индексация словарей переводов

## ⚠️ ЖЕЛЕЗНОЕ ПРАВИЛО
**НЕ ДЕЛАТЬ АПЕНДЫ И ЭКСТЕНДЫ! Только замены существующих ключей или добавление новых с полной документацией.**

---

## СТРУКТУРА СЛОВАРЕЙ

Три основных словаря:
- `en.json` - Английский (LTR - слева направо)
- `ru.json` - Русский (LTR - слева направо)  
- `he.json` - Иврит (RTL - справа налево)

---

## ИНДЕКСАЦИЯ КЛЮЧЕЙ (пронумерованные)

### СИСТЕМА (System keys) - 1-10
| ID | Ключ | EN | RU | HE | Используется |
|---|---|---|---|---|---|
| 1.1 | `_meta` | Metadata | Метаданные | מטא-נתונים | Заголовок файла |
| 1.2 | `language` | English | Русский | עברית | В _meta: язык системы |
| 1.3 | `direction` | ltr | ltr | rtl | В _meta: направление текста |
| 1.4 | `company_name` | YaM SOFT © | YaM SOFT © | © ימ סוףט  | footer, модальное окно |

### АУТЕНТИФИКАЦИЯ (Authentication) - 20-50
| ID | Ключ | EN | RU | HE | Используется |
|---|---|---|---|---|---|
| 20.1 | `login` | Login | Вход | כניסה | login.html |
| 20.2 | `login_title` | Login to Exam System | Вход в Систему экзаменов | התחבר למערכת בחינות | login.html заголовок |
| 20.3 | `signup_title` | Create Account | Создать Аккаунт | צור חשבון | signup.html заголовок |
| 20.4 | `password` | Password | Пароль | סיסמה | login/signup форма |
| 20.5 | `username` | Username | Имя пользователя | שם משתמש | login/signup форма |
| 20.6 | `email` | Email | Email | דוא"ל | signup форма |
| 20.7 | `first_name` | First Name | Имя | שם פרטי | signup форма |
| 20.8 | `last_name` | Last Name | Фамилия | שם משפחה | signup форма |
| 20.9 | `confirm_password` | Confirm Password | Подтвердить пароль | אשר סיסמה | signup форма |

### ЭКЗАМЕНЫ (Exams) - 100-200
| ID | Ключ | EN | RU | HE | Используется | Hardcoded было |
|---|---|---|---|---|---|---|
| 100.1 | `exam_name` | Exam | Экзамен | בחינה | exam.html заголовок | - |
| 100.2 | `question_number` | Question | Вопрос | שאלה | exam_script.js вывод | Исходно: hardcoded |
| 100.3 | `of` | of | из | מתוך | exam_script.js вывод "Q 1 of 10" | Исходно: hardcoded |
| 100.4 | `previous` | Previous | Назад | הקודם | exam.html кнопка (+ стрелка ← в JS) | exam.html hardcoded "← Previous" |
| 100.5 | `next` | Next | Далее | הבא | exam.html кнопка (+ стрелка → в JS) | exam.html hardcoded "Next →" |
| 100.6 | `submit_exam` | Submit Exam | Отправить экзамен | שלח בחינה | exam.html кнопка | - |
| 100.7 | `start_exam` | Start Exam | Начать экзамен | התחל בחינה | exam.html кнопка + student_exam_session.html | - |
| 100.8 | `warning_do_not_leave` | Do NOT leave... | Не уходите... | אל תעזבו... | exam.html предупреждение | - |
| 100.9 | `answer` | Answer | Ответ | תשובה | Общее использование | - |
| 100.10 | `correct_answer` | Correct Answer | Правильный ответ | תשובה נכונה | Общее использование | - |

### ЭКЗАМЕНЫ - СТУДЕНЧЕСКАЯ ФОРМА (Exam Student Form) - 101-110
| ID | Ключ | EN | RU | HE | Используется |
|---|---|---|---|---|---|
| 101.1 | `exam_instructions` | Instructions: | Инструкции: | הוראות: | student_exam_session.html (line 274) |
| 101.2 | `enter_name_above` | Enter your name above | Введите ваше имя выше | הכנס את שמך למעלה | student_exam_session.html (line 276) |
| 101.3 | `click_start_exam_instruction` | Click START EXAM - exam will load immediately | Нажмите НАЧАТЬ ЭКЗАМЕН... | לחץ על התחל בחינה... | student_exam_session.html (line 277) |
| 101.4 | `answer_all_questions_instruction` | Answer all questions | Ответьте на все вопросы | ענה על כל השאלות | student_exam_session.html (line 278) |
| 101.5 | `click_submit_instruction` | Click SUBMIT when finished | Нажмите ОТПРАВИТЬ... | לחץ על שלח כשתסיים | student_exam_session.html (line 279) |
| 101.6 | `exam_completed` | Exam Completed | Экзамен завершен | בחינה הושלמה | student_exam_session.html результаты |
| 101.7 | `exam_submitted_successfully` | your exam was submitted successfully | ваш экзамен был успешно отправлен | הבחינה שלך נשלחה בהצלחה | student_exam_session.html результаты |

### ЯЗЫКИ И СЕЛЕКТОР (Languages) - 150-160
| ID | Ключ | EN | RU | HE | Используется |
|---|---|---|---|---|---|
| 150.1 | `english` | English | Английский | אנגלית | base.html language selector |
| 150.2 | `russian` | Русский | Русский | רוסית | base.html language selector |
| 150.3 | `hebrew` | עברית | Иврит | עברית | base.html language selector |

---

## ДОКУМЕНТАЦИЯ ИСПОЛЬЗОВАНИЯ

### exam.html - Регионы с переводами
```html
<!-- REGION 1: Pre-exam form (строки 10-30) -->
<h1 id="exam-title" data-i18n="exam_name">Exam</h1>
<!-- KEY: exam_name - используется для заголовка перед началом экзамена -->

<!-- REGION 2: Warning alert (строки 14-15) -->
<p data-i18n="warning_do_not_leave">Do NOT leave the exam page until submitted</p>
<!-- KEY: warning_do_not_leave -->

<!-- REGION 3: Input labels (строки 17-23) -->
<label for="first-name" data-i18n="first_name">First Name</label>
<label for="last-name" data-i18n="last_name">Last Name</label>
<!-- KEYS: first_name, last_name -->

<!-- REGION 4: Start button (строка 26) -->
<button id="start-btn" class="btn btn-primary" data-i18n="start_exam">Start Exam</button>
<!-- KEY: start_exam -->

<!-- REGION 5: Navigation buttons (строки 47-49) -->
<!-- ВАЖНО: Текст кнопок заполняется через updateTranslations() в exam_script.js -->
<!-- Стрелки добавляются динамически! -->
<button id="prev-btn" class="btn btn-secondary" style="display: none;"><span data-i18n="previous"></span></button>
<button id="next-btn" class="btn btn-secondary"><span data-i18n="next"></span></button>
<button id="submit-btn" class="btn btn-success" style="display: none;" data-i18n="submit_exam"></button>
<!-- KEYS: previous (+ ← стрелка в JS), next (+ → стрелка в JS), submit_exam -->
```

### exam_script.js - Логика переводов
```javascript
// LINE 282: Вывод номера вопроса
// KEY MAPPING: question_number + of
${i18n.t('question_number')} ${question.number} ${i18n.t('of')} ${this.questions.length}
// РЕЗУЛЬТАТ: "Question 1 of 10" / "Вопрос 1 из 10" / "שאלה 1 מתוך 10"

// LINE 57-90: updateTranslations()
// Функция добавляет стрелки к кнопкам:
prevBtn.innerHTML = `← <span data-i18n="previous">${prevSpan.textContent}</span>`;
nextBtn.innerHTML = `<span data-i18n="next">${nextSpan.textContent}</span> →`;
// Стрелка ← для RTL (иврит) может быть обработана CSS автоматически
```

---

## ПРАВИЛА ДОБАВЛЕНИЯ НОВЫХ КЛЮЧЕЙ

1. **Дать ID** в формате `XXX.Y` где XXX - категория, Y - порядковый номер
2. **Добавить в таблицу индекса** с ремаркой использования
3. **Добавить во все три файла** (en.json, ru.json, he.json) одновременно
4. **Документировать в коде**, где используется ключ (data-i18n атрибут)
5. **Обновить этот файл** с новой записью

---

## ПРОЦЕСС ВОССТАНОВЛЕНИЯ

Если словарь испорчен:
1. Посмотреть этот индекс
2. Найти ID поврежденного ключа
3. Восстановить из описания в таблице
4. Проверить все три языка одновременно

---

## ВЕРСИОНИРОВАНИЕ

- **v1.0** (2026-02-03) - Начальная индексация, добавлены ключи для экзамена
  - Переведены вопросы, кнопки, основные элементы
  - Добавлена RTL поддержка (иврит)
  - Документирована логика стрелок в exam_script.js

