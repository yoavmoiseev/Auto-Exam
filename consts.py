# constant values for server.py
import tkinter as tk
from tkinter import messagebox
import os  # Import library for handling file paths 

#================================================================================================
def select_exam_file(exams_folder_name = "Exams"):
    """Opens a GUI form where the user can select a file from the 'Exams' folder."""
    exams_folder = os.path.join(os.path.dirname(__file__), exams_folder_name)  # Path to 'Exams' folder

    # Check if the folder exists
    if not os.path.exists(exams_folder):
        messagebox.showerror("Error", f"Folder '{exams_folder}' not found!")
        return None

    # Get the list of .txt files in the folder
    exam_files = [f for f in os.listdir(exams_folder) if f.endswith('.txt')]

    if not exam_files:
        messagebox.showwarning("No Exams Found", "No exam files found in the 'Exams' folder.")
        return None

    # Function to handle selection
    def on_select():
        """Handles the selection of a file and closes the window."""
        selected_index = listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select an exam file.")
            return
        selected_file.set(exam_files[selected_index[0]])  # Store selected file
        root.destroy()  # Close window

    # Create the main GUI window
    root = tk.Tk()
    root.title("Select Exam File")
    root.geometry("300x250")

    # Create a StringVar to store the selected file
    selected_file = tk.StringVar()

    # Create and pack a label
    tk.Label(root, text="Select an Exam File:", font=("Arial", 12)).pack(pady=10)

    # Create and pack a listbox
    listbox = tk.Listbox(root, selectmode=tk.SINGLE, font=("Arial", 10), height=len(exam_files))
    for file in exam_files:
        listbox.insert(tk.END, file)
    listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    # Create and pack a select button
    tk.Button(root, text="Select", command=on_select).pack(pady=10)

    # Run the event loop
    root.mainloop()

    # Return the full file path if a file was selected
    return os.path.join(exams_folder, selected_file.get()) if selected_file.get() else None
#================================================================================================

# Constants
exam_folder_name = "Exams"  # Name of the folder containing exam files
exam_full_path = select_exam_file(exam_folder_name)
exam_txt_file_name = os.path.basename(exam_full_path)[:-4]

server_port = 8000

grades_file_name = 'GRADES.txt'

start_of_question_mark = "."
end_of_question_mark = '?'


html_pre_exam_page = """
            <!-- Notification Page before starting the exam -->
                            
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
                            <p style="color: red; font-weight: bold; font-size: 18px; text-align: center; direction: rtl;">
                     אל תעזוב את דף הבחינה עד שהבחינה תוגש, אחרת היא תבוטל
                </p>

                
                <button onclick="loadExam()" style="display: block; margin: 50px auto; font-size: 50px; padding: 20px 40px; background-color: red; color: white; border: none; border-radius: 10px; cursor: pointer;">
                    Start the Exam
                </button>


            </div>

            <!-- Exam Form Section (Initially Hidden) -->
            <div id="exam-form" style="display: none;">

            """


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

js_script_file_name = "script.js"

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


html_js = read_js()

         

html_middle = """</script>
            </head><body> 

            <h1>Exam-""" + exam_txt_file_name + """</h1>
        
            <form action='/submit' method='post' onsubmit='return validateForm()'>
            """

user_name_eng = """
                <br>
                <label style='font-size: 20px; margin-right: 20px;'>First Name: <input type='text' name='first_name' required></label>
                <label style='font-size: 20px; margin-right: 20px;'>Last Name: <input type='text' name='second_name' required></label>
                """

user_name_heb = """
                <br>
                <label style='font-size: 20px; margin-right: 20px;'>שם פרטי: <input type='text' name='first_name' required></label>
                <label style='font-size: 20px; margin-right: 20px;'>שם משפחה: <input type='text' name='second_name' required></label>
                """
              
user_details_textboxes = """                
                <!-- Hidden input fields for transfering values from client to server -->
                <input type='hidden' id='cheating_attempts_input' name='cheating_attempts'> 
                <input type='hidden' id='minutes_input' name='minutes'>
                <input type='hidden' id='seconds_input' name='seconds'>

                <br><br>
                <div>Time: <span id="minutes">00</span>:<span id="seconds">00</span></div>
                <br><br>
                """


submit_button = """
                    <input type='submit' value='Submit Exam' style='font-size: 15px; font-weight: bold; padding: 15px 30px; background-color: red; color: white; border-radius: 20px; cursor: pointer;'>
                    </form></body></html>
                """




