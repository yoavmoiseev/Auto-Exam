# 📚 Exam System – Multilingual Online Exam & Proctoring Platform

A full-featured online examination management system with built-in anti-cheating (proctoring), multi-language support, and responsive design.

---

## ✨ Key Features

### 👨‍🏫 For Teachers

* Create and manage exams
* View student results in real time
* Monitor active exam sessions
* Download results as ZIP archives
* Review cheating attempts

---

### 👨‍🎓 For Students

* Take exams with multiple question types
* Support for open-ended questions (textarea)
* Support for multiple-choice questions (radio buttons)
* Exam timer
* Auto-save answers
* View final score after completion

---

## 🔒 Security & Proctoring

* Blocking **Ctrl+C (copying)**
* Blocking **Google Translate** (optional)
* Fullscreen mode (optional)
* Logging cheating attempts
* Tracking exam duration
* HTML reports with cheating activity

---

## 🌍 Localization

* English (en)
* Russian (ru)
* Hebrew (he) with RTL support
* Easily extensible translation system

---

## 📱 Responsive Design

* Desktop (>768px): full results table
* Tablet (480–768px): optimized layout
* Mobile (<480px): card-based UI with accessible buttons

---

## 🚀 Quick Start

### Local Setup (Windows / Mac / Linux)

```bash
# 1. Clone repository
git clone https://github.com/yoavmoiseev/Auto-Exam.git
cd Ex

# 2. Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# or (Mac/Linux)
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python app.py
```

Open in browser:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---

### Default Login

* Teacher: `teacher1 / password123`
* Student: enter name on exam page

---

## 📁 Project Structure

* **app.py** – main Flask application
* **services/** – business logic layer
* **templates/** – HTML templates
* **static/** – CSS, JS, media
* **data/translations/** – i18n files
* **Exams/** – sample exam files
* **teachers/** – exam results storage

---

## 🛠️ Tech Stack

* **Backend:** Python 3.8+, Flask
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Encoding:** UTF-8 (full Unicode support)
* **i18n:** JSON-based translations
* **Storage:** File-based (text files)

---

## 📋 Exam File Format

Exams are stored as `.txt` files:

```
1. Question?
A) Answer 1
B) Answer 2
C) Correct answer
D) Answer 4

2. Open question?
Open Question
Programming task:
Write a Python function
```

---

## 🎨 Localization

To add a new language:

```bash
cp data/translations/en.json data/translations/xx.json
```

Then update:

```python
SUPPORTED_LANGUAGES = ['en', 'ru', 'he', 'xx']
```

---

## 📊 Results & Reports

**GRADES.txt**

```
2026 February 03 16-05-49 | Yoav_Moiseev | Score: 85% | Cheat: 0 | Duration: 5m 23s
```

Includes:

* Score
* Cheating attempts
* Duration

Additional reports:

* Student HTML reports
* Cheat_Attempts.html

---

## 🔧 Configuration (consts.py)

```python
SUPPORTED_LANGUAGES = ['en', 'ru', 'he']
DEFAULT_LANGUAGE = 'en'

ENABLE_PROCTORING = True
BLOCK_TRANSLATION = False
FULLSCREEN_MODE = False

FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000
```

---

## 🚀 Deployment

Supports deployment on VM (e.g., Ubuntu 22.04, Oracle Cloud).
See `DEPLOYMENT.md` for full instructions.

---

## 🐛 Troubleshooting

**Port already in use**

```bash
lsof -i :5000
kill -9 <PID>
```

**Module not found**

```bash
pip install -r requirements.txt
```

**Encoding issues**

```bash
iconv -f CP1252 -t UTF-8 file.txt -o file_utf8.txt
```

---

## 📝 Recent Updates (Feb 3, 2026)

* Mobile results UI
* Google Translate blocking (optional)
* Fullscreen mode (optional)
* Improved copy protection
* Fixed GRADES.txt format

---

## 🤝 Contributing

* Fork repository
* Create feature branch
* Commit changes
* Open Pull Request

---

## 📧 Contact

* GitHub: yoavmoiseev
* Repository: Auto-Exam

---

## 📄 License

MIT License

---

## ✅ Status

Production-ready (v1.0)
Last updated: February 3, 2026
Supported OS: Windows, macOS, Linux


Скажи 👍
