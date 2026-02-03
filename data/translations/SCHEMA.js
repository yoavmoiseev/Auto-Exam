/**
 * TRANSLATIONS SCHEMA - Описание структуры каждого JSON файла
 * 
 * ⚠️ ВАЖНО: JSON не поддерживает комментарии! 
 * Эта схема - для справки. Используй TRANSLATIONS_INDEX.md для отслеживания.
 * 
 * СТРУКТУРА КАЖДОГО ФАЙЛА (en.json, ru.json, he.json):
 * {
 *   "_meta": {
 *     "language": "Код языка - English/Русский/עברית",
 *     "direction": "ltr или rtl"
 *   },
 *   
 *   // === АУТЕНТИФИКАЦИЯ (ID 20.x) ===
 *   "login": "...",
 *   "password": "...",
 *   ...
 * 
 *   // === ЭКЗАМЕНЫ (ID 100.x) ===
 *   "exam_name": "...",
 *   "question_number": "...",   // ID 100.2 - Используется в exam_script.js:282
 *   "of": "...",                // ID 100.3 - Используется в exam_script.js:282
 *   "previous": "...",          // ID 100.4 - exam.html + JS стрелка ← 
 *   "next": "...",              // ID 100.5 - exam.html + JS стрелка →
 *   "submit_exam": "...",       // ID 100.6
 *   ...
 * }
 * 
 * ОБНОВЛЕНО: 2026-02-03
 * Версия словаря: 1.0
 */

// Текущее использование в коде:

// FILE: exam.html
// - data-i18n="exam_name" (line ~12)
// - data-i18n="warning_do_not_leave" (line ~15)
// - data-i18n="first_name" (line ~18)
// - data-i18n="last_name" (line ~21)
// - data-i18n="start_exam" (line ~26)
// - data-i18n="previous" (line ~47) [+ стрелка ← в JS]
// - data-i18n="next" (line ~48) [+ стрелка → в JS]
// - data-i18n="submit_exam" (line ~49)

// FILE: exam_script.js
// - i18n.t('question_number') (line 282)
// - i18n.t('of') (line 282)
// - updateTranslations() добавляет стрелки к кнопкам (line 57-90)

// FILE: base_student.html
// - data-i18n="company_name" (footer, line ~72)

// FILE: base.html (основной шаблон)
// - data-i18n="company_name" (footer + modal)
// - data-i18n="english" (language selector)
// - data-i18n="russian" (language selector)
// - data-i18n="hebrew" (language selector)

