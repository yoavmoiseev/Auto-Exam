# Teacher Guide - Online Exam System

## What is this program?

This is a website where you can create exams for your students online. Students take the exam on their computer, and you see their results automatically.

## Where does it work?

The website is: **ex.yamsoft.org**

You can open it on any computer with internet - no installation needed.

## How to get started?

1. **Sign Up**: Create your teacher account with username and password
2. **Log In**: Enter your username and password
3. **Add Exams**: Upload exam files from your computer
4. **Students Take Exams**: Give students the website link and exam code
5. **See Results**: Check student answers and scores in your dashboard

---

## How to create an exam file?

Exams are simple text files (`.txt`) that you write on your computer.

### Basic Rules:

1. **Questions start with a number and a dot**
   - Example: `1. What is Python?`
   - Example: `2. Which answer is correct?`

2. **Answers go on the next lines**
   - Write one answer per line
   - The **first answer is always the correct answer**

3. **Use empty lines to separate questions** (optional but makes it clearer)

---

## Example 1: Simple Multiple Choice Exam

```
1. What is the capital of France?
Paris
London
Berlin
Madrid

2. How many days are in a week?
7
5
10
6

3. What color is the sky?
Blue
Red
Green
Yellow
```

**How it works:**
- Question 1: Correct answer is "Paris" (first answer)
- Question 2: Correct answer is "7" (first answer)
- Question 3: Correct answer is "Blue" (first answer)

The system will **shuffle** the answers randomly for each student, so they don't always see the correct answer first.

---

## Example 2: Open Questions (Student Types Answer)

If a question has **no answers after it**, the system automatically makes it an **open question**. The student will type their answer in a text box.

```
1. What is your favorite color and why?

2. Explain what a computer is in your own words.

3. Describe three things you learned this week.
```

**How it works:**
- No answer options = Open question
- Student writes their own answer
- You must grade these answers manually (the system cannot grade open answers automatically)

---

## Example 3: Programming Tasks (Special Open Questions)

For questions where you want to show **code**, **examples**, or **long instructions**, use the special marker: `Programming task:`

Put this marker as the **first line after the question**, then add your code or instructions.

```
1. What will happen if we run this code?
Programming task:
python
x = "5"
y = 2
print(x + y)

2. Write a program that prints "Hello World"
Programming task:
Example:
Input: (press Enter)
Output: Hello World

3. Fix the error in this code:
Programming task:
def add_numbers(a b):
    return a + b
print(add_numbers(5, 3))
```

**How it works:**
- The marker `Programming task:` tells the system this is a special question
- Everything after the marker is shown to the student (code, examples, instructions)
- The marker itself is **hidden** from students
- Student sees a big text box to type their answer

---

## Example 4: Mixed Exam (Multiple Choice + Open Questions)

You can mix different question types in one exam:

```
1. What is 2 + 2?
4
5
3
6

2. What programming language do you want to learn and why?

3. Which one is a valid Python variable name?
my_variable
2variable
my-variable
class

4. Write a Python program that prints your name
Programming task:
Example:
Input: (none needed)
Output: My name is John
```

**How it works:**
- Question 1 and 3: Multiple choice (first answer is correct)
- Question 2: Open question (student types answer)
- Question 4: Programming task (student writes code)

---

## Supported Languages

The system automatically detects the language of your exam:

- **English**: Use English letters
- **Hebrew**: Use Hebrew letters (עברית)
- **Russian**: Use Cyrillic letters (Русский)

The exam will display with correct text direction (right-to-left for Hebrew, left-to-right for English/Russian).

---

## How to add an exam to the system?

### Method 1: Upload from your computer

1. Save your exam as a `.txt` file on your computer
2. Log in to the website
3. Click the **"Add Exam"** button
4. Click **"Browse Computer"**
5. Select your exam file
6. Click **"View Source"** to check if it looks correct
7. Click **"Student Preview"** to see how students will see it
8. Click **"Exam Data"** to see question count and check for errors
9. If everything looks good, click **"Add Exam"**

### Method 2: Load from examples

1. Click the **"Add Exam"** button
2. Click **"Load from Examples"**
3. Choose an example exam to see how it's formatted
4. You can use it as a template for your own exams

---

## Understanding the preview buttons

When you select an exam file, you see three preview buttons:

### 1. View Source
Shows the **raw text** of your exam file exactly as you wrote it. Use this to check if your formatting is correct.

### 2. Student Preview
Shows how the exam will **look to students** when they take it:
- Multiple choice questions show answer options
- Open questions show a text box
- Programming tasks show the code/instructions and a text box
- Answers are **shuffled** (except for open questions)

### 3. Exam Data
Shows **information about your exam**:
- Total number of questions
- How many multiple choice questions
- How many open questions
- Language detected (English, Hebrew, Russian)
- Any errors or problems found

---

## Common mistakes to avoid

❌ **Wrong:** Question without number and dot
```
What is Python
Answer 1
Answer 2
```

✅ **Correct:** Question WITH number and dot
```
1. What is Python?
Answer 1
Answer 2
```

---

❌ **Wrong:** Answers starting with numbers
```
1. How many days in a week?
1. Seven
2. Five
3. Ten
```

✅ **Correct:** Answers WITHOUT numbers
```
1. How many days in a week?
Seven
Five
Ten
```

---

❌ **Wrong:** Correct answer not first
```
1. What is 2+2?
3
5
4
6
```

✅ **Correct:** Correct answer FIRST
```
1. What is 2+2?
4
3
5
6
```

---

## How students take the exam

1. Student goes to **ex.yamsoft.org**
2. Student enters the **exam code** you give them
3. Student sees the questions one by one or all at once (depends on exam settings)
4. Student clicks submit when done
5. **Multiple choice questions** are graded automatically
6. **Open questions** you must grade manually

---

## How to see student results

1. Log in to your account
2. Click **"View Results"** in your dashboard
3. You will see:
   - Student names
   - Exam names
   - Scores (for multiple choice questions)
   - Submission date and time
4. Click on a result to see detailed answers
5. For open questions, you must read and grade them yourself

---

## Important tips

✅ **Always put the correct answer first** - the system will shuffle them for students

✅ **Use clear, simple language** in your questions

✅ **Test your exam** using "Student Preview" before activating it

✅ **Save your exam files** on your computer as backup

✅ **Use Programming task:** for code examples and long instructions

✅ **Empty line between questions** makes your exam easier to read (optional)

❌ **Don't use special symbols** like `@#$%` in question numbers

❌ **Don't forget the dot** after the question number

❌ **Don't mix different languages** in one exam

---

## Quick Reference: Question Types

| Type | How to create | What student sees | Grading |
|------|--------------|-------------------|---------|
| **Multiple Choice** | Question + 2 or more answers | Radio buttons with shuffled answers | Automatic |
| **Open Question** | Question with NO answers after it | Big text box | Manual |
| **Programming Task** | Question + `Programming task:` + code/instructions | Code/instructions + text box | Manual |

---

## Need help?

If you have problems:
1. Check your exam file follows the format rules
2. Use "Exam Data" button to see if there are errors
3. Look at the example exams for correct formatting
4. Make sure your file is saved as `.txt` format

---

## Example exam file you can copy and modify:

```
1. What is your name?

2. What is 5 + 5?
10
15
20
25

3. Write a program that prints "Hello"
Programming task:
Use the print() function in Python
Example: print("Hello")

4. Which is a programming language?
Python
Microsoft Word
Google Chrome
Calculator

5. Explain why learning programming is useful.
```

Save this as `example_exam.txt` and upload it to try the system!

---

**Remember:** This system makes creating and grading exams easier, but YOU are still the teacher. Use it as a tool to help your teaching, not replace it.

Good luck with your exams! 🎓
