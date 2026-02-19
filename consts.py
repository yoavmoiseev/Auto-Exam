# constant values for server.py
import os  # Import library for handling file paths
import select_exam_gui # Tkinter GUI for selecting exam files

# Constants
# Should be overrided by GUI
source_exam = None

# Port number for the server,
# Can be overrided by GUI 
server_port = 8000 # change for multiple instances

open_exam = ["Programming task:", "Open Question/Multiple lines question/task:", "Type your answer here"]

exam_folder_name = "Exams"  # Name of the folder containing exam files

# Tkinter GUI for selecting an exam file from the specified folder
get_data_from_gui = select_exam_gui.select_exam_file(exam_folder_name)

exam_full_path = get_data_from_gui[0]  # Full path of the selected exam file
# The examinator can limit the number of questions that will be 
# presented to user from the entire exam file.
# The question selection is random from the entire exam file questions list.

limited_questions_number = get_data_from_gui[1]  # Number of questions to be selected

shuffle_exam = get_data_from_gui[2]

# Get the file name without the path and extension
exam_txt_file_name = os.path.basename(exam_full_path)[:-4]

question_format_description = """
!!!You can NOT procced with this exam file!!!
There are incorrectly formatted questions in the exam file!!!
The question should start with NUMBER and DOT- '1. Write three reason for...'
Answears can NOT start with number and dot
Multipule lines questions should include
  Programming task:    text on second line!"""

# Use regular expressions to identify the question format in the exam file
# d+ - one or more digits
# \. - a period (dot) character
# \s - whitespace character (space, tab, newline, etc.)
# .* - zero or more characters (any character except newline)
# \? - a question mark character
# The pattern matches lines that start with a number followed by:
# a period, a space, and then a question mark.
# Current question format-  '1. What is a motherboard?'
question_pattern = r"^[\u200E\u200F\u202A-\u202E]*\d+\.\s.*"   # allow optional bidi marks before number

grades_file_name = 'GRADES.txt'

all_exams_txt = 'All_Exams.txt'

open_exam_grade = "unknown yet, exam will be evaluated later"

exam_submitted = "your exam was submitted successfully"

# The question format in the exam file
start_of_question_mark = "."

global_delimiter = "############################################################################\n\n"
local_delimiter =  "\n----------------------------------------------------------------------------\n"

# HTML form with warning messages before starting the exam
html_pre_exam_page = """
            <!-- Warrning page before starting the exam -->
                            
            <div id="notification">
                <h1 style="font-weight: bold; font-size: 50px; text-align: center;">
                    """ + exam_txt_file_name + """ 
                </h1>
                    
                <p style="color: red; font-weight: bold; font-size: 18px; text-align: center;">
                    Do NOT leave the exam page until the exam is submitted, otherwise, the exam will be dismissed
                </p>
                <p style="color: red; font-weight: bold; font-size: 18px; text-align: center;">
                    НЕ покидайте страницу экзамена, пока он не будет отправлен, иначе он будет аннулирован
                </p>
                            <p style="color: red; font-weight: bold; font-size: 24px; text-align: center; direction: rtl;">
                     אל תעזוב את דף הבחינה עד שהבחינה תוגש, אחרת היא תבוטל
                </p>

                </p>
                            <p style="color: red; font-weight: bold; font-size: 20px; text-align: center; direction: rtl;">
                       השתמש ב-CTRL + SHIF ימני או SHIFT שמאלי לסרוגים לשינוי כיוון הטקסט הנכתב  
                 </p>


                
                <button onclick="loadExam()" style="display: block; margin: 50px auto; font-size: 50px; padding: 20px 40px; background-color: red; color: white; border: none; border-radius: 10px; cursor: pointer;">
                    Start the Exam
                </button>


            </div>

            <!-- Exam Form Section (Initially Hidden) -->
            <div id="exam-form" style="display: none;">

            """

# HTML form with exam questions and user details
html_start = """
        <head>
            <meta charset='UTF-8'>
            <title>Exam</title>
            <style>
            body {
                background-color: lightgray;
            }
            </style>
            <script>
            """

# JavaScript code for the exam form
# This code is responsible for handling the exam timer and form validation
js_script_file_name = "script.js"

# Read the JavaScript file and store its content in a variable
def read_js(file_name = js_script_file_name):
    """
    Read the JS file and return it as a string.
    :param file_name: Name of the JS file
    :return: JS file content as a string
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
    abs_path = os.path.join(script_dir, file_name)  # Join script directory with file name
    
    with open(abs_path, 'r', encoding="utf-8") as file:
        js_content = file.read()  # Read file content
    return js_content

# Add the JavaScript code to the HTML form
html_js = read_js()

# Combine the HTML and JavaScript code       
html_middle = """</script>
            </head><body> 

            <h1>""" + exam_txt_file_name + """</h1>
        
            <form action='/submit' method='post' onsubmit='return validateForm()'>
            """
# User details textboxes for English exam from
user_name_eng = """
                <br>
                <label style='font-size: 20px; margin-right: 20px;'>First Name: <input type='text' name='first_name' required></label>
                <label style='font-size: 20px; margin-right: 20px;'>Last Name: <input type='text' name='second_name' required></label>
                """
# User details textboxes for Hebrew exam form
user_name_heb = """
                <br>
                <label style='font-size: 20px; margin-right: 20px;'>שם פרטי: <input type='text' name='first_name' required></label>
                <label style='font-size: 20px; margin-right: 20px;'>שם משפחה: <input type='text' name='second_name' required></label>
                """
# Values that should be passed to the server when the exam is submitted             
user_details_textboxes = """                
                <!-- Hidden input fields for transfering values from client to server --> 
                <input type='hidden' id='minutes_input' name='minutes'>
                <input type='hidden' id='seconds_input' name='seconds'>

                <br><br>
                <div>Time: <span id="minutes">00</span>:<span id="seconds">00</span></div>
                <br><br>
                """

# The Submit button then sends the form data to the server for processing
# The form uses the POST method to send the data to the server at the '/submit' endpoint
# The form includes a JavaScript function to validate the input before submission
submit_button = """
                    <input type='submit' value='Submit Exam' style='font-size: 15px; font-weight: bold; padding: 15px 30px; background-color: red; color: white; border-radius: 20px; cursor: pointer;'>
                    </form></body></html>
                """




