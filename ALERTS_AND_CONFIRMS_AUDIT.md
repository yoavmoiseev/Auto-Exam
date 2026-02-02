# Alert & Confirm Messages Audit
## Полный список всех сообщений браузера (alert/confirm)

---

## СТАТУС ПЕРЕВОДА

### ✅ УЖЕ ПЕРЕВЕДЕНЫ (используют i18n.t()):
1. **base.html:150** - Logout confirmation
   - i18n key: `confirm_logout`
   - Статус: ✅ Переведено
   
2. **teacher_results.html:175** - Delete folder confirmation
   - i18n key: `confirm_delete_folder`
   - Статус: ✅ Переведено
   
3. **teacher_results.html:191** - Folder deleted alert
   - i18n key: `folder_deleted`
   - Статус: ✅ Переведено
   
4. **teacher_results.html:194** - Error alert
   - i18n key: `error`
   - Статус: ✅ Переведено
   
5. **teacher_results.html:198** - Error alert
   - i18n key: `error`
   - Статус: ✅ Переведено

6. **teacher_results.html:205** - Delete all confirmation
   - i18n key: `confirm_delete_all`
   - Статус: ✅ Переведено

7. **teacher_results.html:211** - Delete all double confirmation
   - i18n key: `confirm_delete_all_double`
   - Статус: ✅ Переведено

8. **teacher_results.html:223** - All folders deleted alert
   - i18n key: `all_folders_deleted`
   - Статус: ✅ Переведено

9. **teacher_dashboard.html:288** - End exam confirmation
   - Текст: `'Are you sure you want to end this exam?\n\nStudents will not be able to access it anymore.'`
   - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
   - Статус: ❌ ТРЕБУЕТ ПЕРЕВОДА
   - Рекомендуемый ключ: `confirm_end_exam`

10. **teacher_dashboard.html:300** - Exam ended successfully
    - Текст: `'Exam ended successfully'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Статус: ❌ ТРЕБУЕТ ПЕРЕВОДА
    - Рекомендуемый ключ: `exam_ended_successfully`

11. **teacher_dashboard.html:303** - Error ending exam
    - Текст: `'Error: ' + data.message`
    - i18n key: `error` (частично)
    - Статус: ⚠️ ТРЕБУЕТ ДОРАБОТКИ

12. **teacher_dashboard.html:307** - Error ending exam
    - Текст: `'Error ending exam'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Статус: ❌ ТРЕБУЕТ ПЕРЕВОДА
    - Рекомендуемый ключ: `error_ending_exam`

13. **teacher_dashboard.html:283** - Clipboard copy
    - Текст: `'URL copied to clipboard!'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Статус: ❌ ТРЕБУЕТ ПЕРЕВОДА
    - Рекомендуемый ключ: `url_copied_clipboard`

---

### ❌ НЕ ПЕРЕВЕДЕНЫ (hardcoded текст):

14. **exam_settings_modal.html:344** - Select folder error
    - Текст: `'Please select a folder to append to, or choose "Create NEW folder"'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `select_folder_error`

15. **exam_settings_modal.html:373** - Generic error
    - Текст: `'Error: ' + result.message`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `error_generic`

16. **exam_settings_modal.html:377** - Failed to start exam
    - Текст: `'Failed to start exam'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `failed_start_exam`

17. **teacher_exams.html:95** - Delete exam confirmation
    - Текст: `'Are you sure you want to delete: ' + examName + '?'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `confirm_delete_exam`

18. **teacher_exams.html:102** - Exam deleted successfully
    - Текст: `'Exam deleted successfully'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `exam_deleted_successfully`

19. **teacher_exams.html:105** - Error deleting exam
    - Текст: `'Error: ' + data.message`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `error_deleting_exam`

20. **teacher_exams.html:110** - Error deleting exam (generic)
    - Текст: `'Error deleting exam'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `error_deleting_exam_generic`

21. **signup.html:110** - Signup message
    - Текст: `result.message` (переменное содержимое)
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО (зависит от сервера)
    - Статус: ⚠️ ТРЕБУЕТ УТОЧНЕНИЯ

22. **student_exam_session.html:365** - Error loading questions
    - Текст: `'Error loading exam questions'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `error_loading_questions`

23. **student_exam_session.html:369** - Generic error
    - Текст: `'An error occurred'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `error_occurred`

24. **student_exam_session.html:474** - Answer all questions
    - Текст: `'Please answer all questions before submitting'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `answer_all_questions`

25. **student_exam_session.html:504** - Submit exam confirmation
    - Текст: `'Are you sure you want to submit your exam?\n\nYou cannot change your answers after submission.'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `confirm_submit_exam`

26. **student_exam_session.html:546** - Error submitting exam
    - Текст: `'Error submitting exam: ' + data.message`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `error_submitting_exam`

27. **student_exam_session.html:550** - Failed to submit exam
    - Текст: `'Failed to submit exam'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `failed_submit_exam`

28. **static/proctoring.js:31** - Enter name error
    - Текст: `'Please enter your first and last name'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `enter_name_error`

29. **static/proctoring.js:83** - Error error
    - Текст: `'Error: ' + data.message`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `error_generic`

30. **static/proctoring.js:87** - An error occurred
    - Текст: `'An error occurred'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `error_occurred`

31. **static/proctoring.js:351** - Error submitting exam
    - Текст: `'Error submitting exam: ' + data.message`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `error_submitting_exam`

32. **static/proctoring.js:355** - Error submitting exam
    - Текст: `'An error occurred while submitting the exam'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `error_submitting_exam_generic`

---

### ⚠️ УЖЕ ИСПОЛЬЗУЮТ i18n.t() (но проверить наличие ключей):

33. **static/js/exam_script.js:185** - Student name required
    - i18n key: `student_name` + `required`
    - Статус: ✅ Используют i18n

34. **static/js/exam_script.js:221** - Error with message
    - i18n key: `error`
    - Статус: ✅ Используют i18n

35. **static/js/exam_script.js:236** - Error uploading
    - i18n key: `error_uploading`
    - Статус: ✅ Используют i18n

36. **static/js/exam_script.js:377** - Confirm submit
    - i18n key: `confirm_submit`
    - Статус: ✅ Используют i18n

37. **static/js/exam_script.js:403** - Exam failed
    - i18n key: `exam_failed`
    - Статус: ✅ Используют i18n

38. **static/js/exam_script.js:408** - Error
    - i18n key: `error`
    - Статус: ✅ Используют i18n

39. **static/js/exam_script.js:454** - Alert reason
    - Текст: `reason` (переменное)
    - Статус: ⚠️ ТРЕБУЕТ УТОЧНЕНИЯ

---

### ⚠️ СПЕЦИАЛЬНЫЕ СЛУЧАИ (exam-specific во время exam monitoring):

40. **script.js:38** - Answer all questions (во время экзамена)
    - Текст: `'Please answer all questions before submitting the exam.'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `answer_all_questions_exam`

41. **script.js:144** - Action disabled during exam
    - Текст: `'This action is disabled during the exam!'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `action_disabled_exam`

42. **script.js:151** - Right-click disabled during exam
    - Текст: `'Right-click is disabled during the exam!'`
    - i18n key: ❌ НЕ ПЕРЕВЕДЕНО
    - Рекомендуемый ключ: `rightclick_disabled_exam`

---

## ИТОГОВАЯ СТАТИСТИКА:

- **Всего найдено сообщений**: 42
- **✅ Уже переведены**: 8
- **❌ Требуют перевода**: 28
- **⚠️ Требуют уточнения/проверки**: 6

---

## ПЛАН ДЕЙСТВИЙ:

### ЭТАП 1: Добавить новые ключи в JSON файлы
- Добавить 28 новых ключей в `en.json`, `ru.json`, `he.json`

### ЭТАП 2: Обновить код в шаблонах
- Заменить hardcoded alert/confirm на использование `window.i18n?.t('key')`
- Обновить 28 мест в HTML и JS файлах

### ЭТАП 3: Проверить существующие ключи
- Убедиться что все используемые ключи существуют в переводах
