from http.server import BaseHTTPRequestHandler, HTTPServer  # Import necessary classes to create an HTTP server
import socket  # Import library to handle IP addresses
import urllib.parse  # Import library to handle URL-encoded data (used in POST requests)
import os  # Import library for handling file paths
import datetime  # Import library to handle date and time
import random
import re
import consts

class ExamHandler(BaseHTTPRequestHandler):  # Define a class to handle HTTP requests

    source_exam = None
    question_answer_dict = None
    exmam_file_path = None
    


#==================================================================================================
    def do_GET(self):  # Handle GET requests (when the user opens the exam page)
        if self.path == '/':  # If the user accesses the root URL ('/')
            self.send_response(200)  # Send HTTP 200 (OK) response
            self.send_header("Content-Type", "text/html; charset=utf-8")  # Set content type to UTF-8 encoded HTML
            self.end_headers()  # End HTTP headers

            
            # Use content if available, otherwise read and cache it
            if not ExamHandler.source_exam:
                ExamHandler.source_exam = self.read_exam_txt_file()

            # Use question-answer dictionary if available
            if not ExamHandler.question_answer_dict:
                ExamHandler.question_answer_dict = self.build_question_answer_dict(ExamHandler.source_exam)


            shuffled_exam = self.shuffle_exam_lines(ExamHandler.source_exam)  # Shuffle the exam questions and answers
            
            html_form = self.build_exam_html_from_txt(shuffled_exam)  # Build the html exam form from the text file


            self.wfile.write(html_form.encode('utf-8'))  # Send HTML to the client



        else:  # If the URL is not '/', return a 404 error
            self.send_response(404)  # Send HTTP 404 (Not Found)
            self.end_headers()  # End HTTP headers

# =======================================================================================
   
    def count_correct_answers_percent(self, submitted_answers):
        """
        Count the percentage of correct answers in the submitted exam."""

        correct_answers = 0
        for question, answer in submitted_answers.items():
            question = question[question.index(consts.start_of_question_mark):]
            if question in ExamHandler.question_answer_dict \
                and ExamHandler.question_answer_dict[question] == \
                    answer:correct_answers += 1

        total_questions = len(ExamHandler.question_answer_dict)
                                                     # for one digit after dot add  *100,1)
        correct_answers_percent = round((correct_answers / total_questions) * 100) 
        
        return correct_answers_percent

# =======================================================================================

    def build_question_answer_dict(self, lines):
        """
        Takes a list of lines representing a multiple-choice exam and builds a dictionary
        where each key is a question and the value is the first answer.

        Parameters:
        lines (list[str]): List of lines representing the exam.

        Returns:
        dict: A dictionary with questions as keys and the first answer as values.
        """
        question_answer_dict = {}
        current_question = None

        for line in lines:
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            # Detect a question using a number followed by ". " and a "?" in the text
            if re.match(r"^\d+\.\s.*\?", line):
                # Extract the question number
                current_question = line[line.index(consts.start_of_question_mark):] 
            elif current_question and current_question not in question_answer_dict:
                question_answer_dict[current_question] = line

        return question_answer_dict

#========================================================================================
    def read_exam_txt_file(self):
        """
        Opens the exam .txt file and read its content
        return: list of lines from the exam file
        """
        exam_file_path = consts.exam_full_path  # Get absolute path to the exam file
        with open(exam_file_path, 'r', encoding="utf-8") as file:  # Open the file with UTF-8 encoding
            exam_content = file.readlines()  # Read all lines from the file
        return exam_content

#========================================================================================    
    
    def build_exam_html_from_txt(self, exam_content):
    # Build HTML form for the exam
        html_form = consts.html_start
        html_form += consts.html_js
        html_form += consts.html_middle

        question_number = 0  # Counter for questions
        current_question = ""  # Store the current question
        answers = []  # List to store answer options

        for line in exam_content:  # Process each line from the exam file
            line = line.strip()  # Remove leading and trailing whitespace
            if not line:
                continue  # Skip empty lines

            if line.endswith(consts.end_of_question_mark):  # If the line is a question
                if current_question and answers:  # If there's a previous question, add it to the form
                    html_form += f"<fieldset><legend><b>{current_question}</b></legend>"  # Display the question
                    for answer in answers:  # List answers as radio buttons
                        html_form += f"<input type='radio' name='{current_question}' value='{answer}'> {answer}<br>"
                    html_form += "</fieldset>"

                question_number += 1  # Increment question counter
                current_question = line  # Store new question
                answers = []  # Reset answer list
            else:
                answers.append(line)  # Add line as an answer option

        # Add the last question and answers to the form
        if current_question and answers:
            html_form += f"<fieldset><legend><b>{current_question}</b></legend>"
            for answer in answers:
                html_form += f"<input type='radio' name='{current_question}' value='{answer}'> {answer}<br>"
            html_form += "</fieldset>"

        # Add user details fields and submit button
        html_form += consts.user_details_textboxes
        html_form += consts.submit_button

        html_form += "</form></body></html>"

        return html_form

    
#==================================================================================================
    def do_POST(self):  # Handle POST requests (when the exam is submitted)
        if self.path == '/submit':  # Check if the request is to submit answers
            content_length = int(self.headers['Content-Length'])  # Get the length of the submitted data
            post_data = self.rfile.read(content_length)  # Read the submitted form data
            form_data = urllib.parse.parse_qs(post_data.decode())  # Decode and parse form data

            first_name = form_data.get('first_name', [None])[0]  # Get first name
            second_name = form_data.get('second_name', [None])[0]  # Get second name
            cheating_attempts = form_data.get('cheating_attempts', [0])[0]  # Get cheating attempts
            minutes = form_data.get('minutes', [0])[0]  # Get minutes
            seconds = form_data.get('seconds', [0])[0]  # Get seconds
            exam_timer = f"{minutes}:{seconds}"  # Format exam timer

            exam_I_P = self.client_address[0]  # Gets the IP address of the client 

            # Extract questions and selected answers
            submitted_answers = {}
            for question, answers in form_data.items():
                # Ignore personal and hidden info fields
                if question not in ['first_name', 'second_name', 'class', 'e-mail',\
                                    'cheating_attempts','minutes','seconds']:  
                    submitted_answers[question] = answers[0]  # Get the selected answer


            grade = self.count_correct_answers_percent(submitted_answers)

            # Format response for the user
            response_html = f"<html><body><meta charset='UTF-8'><h2>{first_name} {second_name}, your exam was submitted successfully!</h2><h3>Your Answers:</h3><ul>"
            for question, answer in submitted_answers.items():
                response_html += f"<li><b>{question}</b>: {answer}</li>"
            
            response_html += f"<h1>Your grade is: {grade}%</h1>"
            response_html += "</ul></body></html>"
          
            # Save the feedback to an HTML file
            self.save_feedback(first_name, second_name, response_html, grade, exam_timer, exam_I_P,cheating_attempts)
            
            
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(response_html.encode('utf-8'))

    def save_feedback(self, first_name, second_name, response_html, grade,\
                       exam_timer, exam_I_P,cheating_attempts):
        # Get the current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Create the folder name
        folder_name = consts.exam_txt_file_name + " " + current_date
        folder_name = os.path.join(os.path.dirname(__file__), folder_name)

        # Create the folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        # Create the file name using first name, second name, and current time
        current_time = datetime.datetime.now().strftime("%H-%M-%S")
        file_name = f"{first_name}_{second_name}_{current_time}.html"
        file_path = os.path.join(folder_name, file_name)
        
        # Save the response HTML to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response_html)
        
        # Summarize students' grades
        summary_file_path = os.path.join(folder_name, consts.grades_file_name)
        with open(summary_file_path, 'a', encoding='utf-8') as summary_file:
            summary_file.write(f"{current_time}:    {first_name} {second_name}- {grade} \
            Cheat Attepts-{cheating_attempts}     I.P-{exam_I_P}   Duration-{exam_timer} \n")
        
        print(f"{current_time}:    {first_name} {second_name}- {grade} \
        Cheat Attepts-{cheating_attempts}  I.P-{exam_I_P}   Duration-{exam_timer} \n")

    

    def shuffle_exam_lines(self, lines: list[str]) -> list[str]:
        """
        Takes a list of lines representing a multiple-choice exam and shuffles:
        - The order of questions.
        - The order of answers within each question.

        Parameters:
        lines (list[str]): List of lines representing the exam.

        Returns:
        list[str]: A new list of shuffled lines in the same format.
        """
        questions = []
        current_question = None
        current_answers = []

        for line in lines:
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            # Detect a question using a number followed by ". " and a "?" in the text
            if re.match(r"^\d+\.\s.*\?", line):
                # Save previous question-answer set
                if current_question:
                    questions.append((current_question, current_answers))

                current_question = line
                current_answers = []
            else:
                current_answers.append(line)

        # Add the last question-answer set
        if current_question:
            questions.append((current_question, current_answers))

        # Shuffle answers within each question
        for i in range(len(questions)):
            question, answers = questions[i]
            random.shuffle(answers)  # Shuffle answer order
            questions[i] = (question, answers)

        # Shuffle question order
        random.shuffle(questions)

        # Reconstruct the shuffled exam as a list of lines
        shuffled_lines = []
        for index, (question, answers) in enumerate(questions, start=1):
            # Rewrite question number to maintain correct numbering
            question_text = re.sub(r"^\d+", str(index), question, 1)
            shuffled_lines.append(question_text)
            shuffled_lines.extend(answers)
            shuffled_lines.append("")  # Add a blank line for readability

        return shuffled_lines


#==================================================================================================
def get_local_ip():
        """
        Get the local IP address of the machine running the server.
        """
        try:
            # Create a socket connection to an external server
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Use Google's public DNS server
            local_ip = s.getsockname()[0]
            s.close()
        except Exception as e:
            local_ip = "127.0.0.1"  # Fallback to localhost if there's an error
            print(f"Error getting local IP address: {e}")
        
        return local_ip
#==================================================================================================
def run():  # Function to start the server
    server_address = ('', consts.server_port)  # Server listens on all available network interfaces, port taken from consts.py
    httpd = HTTPServer(server_address, ExamHandler)  # Create an HTTP server instance

    print("Server socket", get_local_ip() + ":" + str(consts.server_port))  # Print the server address
    print("Exam name:", consts.exam_txt_file_name)  # Print the exam file name
    httpd.serve_forever()  # Keep the server running indefinitely

if __name__ == '__main__':  # Run the server when the script is executed
    run()