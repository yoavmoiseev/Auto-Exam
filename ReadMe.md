**Auto-Exam**

This is a full-stack development project that includes a Python server, a GUI using Tkinter, and JavaScript, HTML, and CSS for the client-side. The project is an automatic multiple-choice examination system built with a Python server using only standard libraries (`http.server`, `OS`, `random`, `datetime`, `urllib`). It reads a text file with exam questions and answers (the correct answer on top), randomizes them, checks answers, and provides feedback and grades to students. The system also summarizes all students' grades on the server side. The entire project is self-contained, with no additional dependencies, and is very lightweight, at about 100 kilobytes. It runs on Windows 10 and is compatible with Python versions 3.10 and 3.13.

**Features of Version 2:**

1. **Hebrew Language Support** – The system now supports Hebrew, allowing for text and exam-related content to be displayed in Hebrew.
2. **Limiting the Number of Questions** – The system allows for a subset of questions to be displayed to each student. For example, with 40 questions in the exam, each student will see a random selection of 20, ensuring that every student gets differnt questions.
3. **Cheating Tracking System** – The system tracks and counts every time a student tries to copy questions, leave the exam page, refresh the page, or any similar suspicious activity. All these attempts are logged and saved in the student feedback.


