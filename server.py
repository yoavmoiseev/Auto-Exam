from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import urllib.parse
import os
import datetime
import random
import re
import consts


class ExamHandler(BaseHTTPRequestHandler):
    # =============================================================================================
    # Global variables
    source_exam = None
    question_answer_dict = None
    exam_file_path = None
    text_direction = None

    # =============================================================================================
    def log_message(self, format, *args):
        """Override the default log_message method to suppress logging."""
        pass

    # =============================================================================================
    def do_GET(self):
        """Handle GET requests (when the user opens the exam page)."""
        if self.path == '/': # the main exam page
            self._handle_exam_page_request()
        elif self.path == '/favicon.ico': # Dissable favicon requests
            self._handle_favicon_request()
        else:
            self._handle_404_request() # page not found

    def _handle_exam_page_request(self):
        """Serve the exam page to the client."""
        self.send_response(200) # OK
        self.send_header("Content-Type", "text/html; charset=utf-8") # HTML content
        self.end_headers() # end of headers

        if not ExamHandler.source_exam: # read the exam file if it hasn't been read yet
            ExamHandler.source_exam = self._read_exam_file()

        if not ExamHandler.question_answer_dict: # build the question-answer dictionary if it hasn't been built yet
            ExamHandler.question_answer_dict = self._build_question_answer_dict(ExamHandler.source_exam)

        # shuffle the questions and answers in the exam
        shuffled_exam = self._shuffle_exam_lines(ExamHandler.source_exam)
        
        # build the HTML form of the exam
        html_form = self._build_exam_html(shuffled_exam)

        try: # send the HTML form to the client
            self.wfile.write(html_form.encode('utf-8'))
        except ConnectionAbortedError:
            print(f"{self.client_address[0]} disconnected before the response was fully sent.")

    def _handle_favicon_request(self):
        """Handle requests for favicon.ico."""
        self.send_response(204) # No Content
        self.end_headers()

    def _handle_404_request(self): # page not found
        """Handle requests for unknown URLs."""
        self.send_response(404)
        self.end_headers()

    # =============================================================================================
    def is_hebrew_text(self, lines):
        """Check if the given lines contain Hebrew text."""
        for line in lines:
            for char in line:
                if "\u0590" <= char <= "\u05FF":  # Hebrew Unicode range
                    return True
        return False

    def set_text_direction(self, exam_content):
        """Set the text direction based on the presence of Hebrew text."""
        if self.is_hebrew_text(exam_content):
            ExamHandler.text_direction = 'dir="rtl"'
        else:
            ExamHandler.text_direction = '' # left-to-right

    # =============================================================================================
    def count_correct_answers_percent(self, submitted_answers):
        """Calculate the percentage of correct answers.
           Compares the submitted answers to the correct answers."""
        correct_answers = 0
        for question, answer in submitted_answers.items(): # check each submitted answer
            question = question[question.index(consts.start_of_question_mark):]
            if question in ExamHandler.question_answer_dict and \
                    ExamHandler.question_answer_dict[question] == answer:
                correct_answers += 1
        # calculate the total number of questions
        total_questions = len(ExamHandler.question_answer_dict)
        # calculate the percentage and round it to the nearest integer
        return round((correct_answers / total_questions) * 100) 
    # =============================================================================================
    def _build_question_answer_dict(self, lines):
        """Build a dictionary of questions and their first answers."""
        question_answer_dict = {}
        current_question = None

        for line in lines:
            line = line.strip() # remove leading and trailing whitespaces
            if not line:
                continue
            
            # Use specific pattern to identify questions
            # Current question format-  '1. What is the primary function of a motherboard?'
            if re.match(consts.question_pattern, line): # check if the line is a question
                # if the line is a question, set it as the current question
                current_question = line[line.index(consts.start_of_question_mark):]
                # if the current question is not in the dictionary, add it
            elif current_question and current_question not in question_answer_dict:
                question_answer_dict[current_question] = line

        return question_answer_dict

    # =============================================================================================
    def _read_exam_file(self):
        """Read the exam file and return its content as a list of lines."""
        with open(consts.exam_full_path, 'r', encoding="utf-8") as file:
            return file.readlines() # list of strings 

    # =============================================================================================
    def _add_exam_questions_and_answers(self, exam_content):
        """Add the exam questions and answers to the HTML form."""
        html_form = ""
        current_question = ""
        answers = []

        for line in exam_content:
            line = line.strip()  # Remove leading and trailing whitespaces
            if not line:
                continue

            # Check if the line is a question
            if line.endswith(consts.end_of_question_mark):
                if current_question and answers:  # If the current question has answers
                    html_form += self._build_question_html(current_question, answers)

                current_question = line
                answers = []
            else:
                answers.append(line)

        # Add the last question and its answers
        if current_question and answers:
            html_form += self._build_question_html(current_question, answers)

        return html_form
    # =============================================================================================
    def _build_exam_html(self, exam_content):
        """Build the HTML form for the exam. Uses the "consts.py" file for the HTML template."""
        # Warrning page before starting the exam
        html_form = consts.html_pre_exam_page

        # Set the text direction based on the exam language
        if ExamHandler.text_direction is None:
            self.set_text_direction(exam_content)
        html_form += f'<html {ExamHandler.text_direction}>'
        # add the page/form code from the consts.py file  
        html_form += consts.html_start + consts.html_js + consts.html_middle

        # Add the exam questions and answers
        html_form += self._add_exam_questions_and_answers(exam_content)
        # Fit user details label to languge
        html_form += consts.user_name_eng if ExamHandler.text_direction == '' else consts.user_name_heb
        # Add the user details textboxes and submit button
        html_form += consts.user_details_textboxes + consts.submit_button
        html_form += "</form></body></html>" # End of form

        return html_form
    
    #======================================================================================
    def _build_question_html(self, question, answers):
        """Generate the HTML code for a single question and its answers."""
        question_html = f"<fieldset><legend><b>{question}</b></legend>"
        for answer in answers:
            question_html += f"<input type='radio' name='{question}' value='{answer}'> {answer}<br>"
        question_html += "</fieldset>"
        return question_html # type string

    # =============================================================================================
    def do_POST(self):
        """Handle POST requests (when the exam is submitted)."""
        if self.path == '/submit':
            self._handle_exam_submission()
    #=====================================================================================
    def _handle_exam_submission(self):
        """Handles the student submitted exam page."""
        # Get the length of the POST data
        content_length = int(self.headers['Content-Length']) 
        # Get the POST data
        post_data = self.rfile.read(content_length)
        # Parse the POST data 
        form_data = urllib.parse.parse_qs(post_data.decode())

        # Get the user's from HTML form
        first_name = form_data.get('first_name', [None])[0]
        second_name = form_data.get('second_name', [None])[0]
        # Get the number of cheating attempts that JS counts
        cheating_attempts = form_data.get('cheating_attempts', [0])[0]
        # Get the exam duration
        minutes = form_data.get('minutes', [0])[0]
        seconds = form_data.get('seconds', [0])[0]
        exam_timer = f"{minutes}:{seconds}"
        # Get the client's IP address and NetBIOS name
        client_ip = self.client_address[0]
        try:
            netbios_name = socket.gethostbyaddr(client_ip)[0]
        except socket.herror:
            netbios_name = "Unknown"
       
        # Build a dictionary of the submitted question answer pairs
        submitted_answers = {
            question: answers[0]
            for question, answers in form_data.items()
            # Skip the user's details and hidden fields
            if question not in ['first_name', 'second_name', 'class', 'e-mail',\
                                 'cheating_attempts', 'minutes', 'seconds']
        }
        # Calculate the grade            
        grade = self.count_correct_answers_percent(submitted_answers)
        # Build the HTML response for the user
        response_html = self._build_response_html(first_name, second_name, submitted_answers, grade)
        # Save the feedback to: folder named as the exam name + date, 
        # add student details to summary file
        self._save_feedback(first_name, second_name, response_html, grade,\
                             exam_timer, client_ip, netbios_name, cheating_attempts)

        try:# Send the response to the client
            self.send_response(200) # OK        
            self.send_header("Content-Type", "text/html; charset=utf-8") # Support Hebrew encoding  
            self.end_headers() # End of headers
            # Send the response html to the client
            self.wfile.write(response_html.encode('utf-8'))
        except ConnectionAbortedError: # Handle client disconnection
            print(f"Client {self.client_address[0]}\
                   disconnected before the response was fully sent.")
    #=================================================================================================
    def _build_response_html(self, first_name, second_name, submitted_answers, grade):
        """Build the results HTML page for the student."""
        # F-string, allows to use variables incide the string using- {}
        response_html = f"<html {ExamHandler.text_direction}><body><meta charset='UTF-8'>"
        response_html += f"<h2>{first_name} {second_name},\
              your exam was submitted successfully!</h2>"
        response_html += "<h3>Your Answers:</h3><ul>"
        # Build the HTML response with the submitted answers
        # Loop through the submitted answers and add them to the HTML response
        for question, answer in submitted_answers.items():
            response_html += f"<li><b>{question}</b>: {answer}</li>"
        # Add the grade to the HTML response
        response_html += f"<h1>Your grade is: {grade}%</h1></ul></body></html>"
        return response_html
    #============================================================================================
    def _save_feedback(self, first_name, second_name, response_html, grade,\
                        exam_timer, client_ip, netbios_name, cheating_attempts):
        """Save the exam feedback and summary to files."""
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        folder_name = os.path.join(os.path.dirname(__file__),\
                                    f"{consts.exam_txt_file_name} {current_date}")

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        current_time = datetime.datetime.now().strftime("%H-%M-%S")
        # Save the student's feedback as HTML file named as the student name and time
        file_name = f"{first_name}_{second_name}_{current_time}.html"
        file_path = os.path.join(folder_name, file_name)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response_html)
        # File that contains the summary of all students' grades
        summary_file_path = os.path.join(folder_name, consts.grades_file_name)
        with open(summary_file_path, 'a', encoding='utf-8') as summary_file:
            summary_file.write(f"{current_time}: {first_name} {second_name}-{grade}  "
                               f"Cheat Attempts-{cheating_attempts} IP-{client_ip} "
                               f"PC_Name-{netbios_name} Duration-{exam_timer}\n")
        # Print notification to console at exam subbmit
        print(f"{current_time}: {first_name} {second_name}-{grade} "
              f"Cheat Attempts-{cheating_attempts} IP-{client_ip} "
              f"PC_Name-{netbios_name} Duration-{exam_timer}")

    # =============================================================================================
    def _shuffle_exam_lines(self, lines):
        """Shuffle the order of questions and answers in the exam."""
        # Tupple (question-str, answers[list of str])
        questions = []  # ("What is 2 + 2?", ["3", "4", "5"])
        current_question = None
        current_answers = [] # List of str
        # Iterate through the lines of the exam file
        for line in lines:
            line = line.strip() # Remove leading and trailing whitespaces
            if not line: # Skip empty lines
                continue
            # Check if the line is a question, format- '1. What is a motherboard?'
            if re.match(consts.question_pattern, line): 
                if current_question: # If there is a current question
                    # Add the question and its answers to the list
                    questions.append((current_question, current_answers))
                current_question = line
                current_answers = []
            else: # If it is an answer
                # Add the answer to the current question's answers
                current_answers.append(line)
        # Add the last question and its answers to the list
        # If there is a current question, add it to the list
        if current_question:
            # Tupple (question-str, answers[list of str]) to the list of questions
            questions.append((current_question, current_answers))

        # Shuffle the questions and answers
        for i in range(len(questions)):
            # Shuffle the answers for each question
            question, answers = questions[i] # Unpack the question and answers from tuple
            random.shuffle(answers)
            questions[i] = (question, answers)

        random.shuffle(questions)

        shuffled_lines = []
        for index, (question, answers) in enumerate(questions, start=1):
            # Uses regular expression to replace the question number with the index 
            question_text = re.sub(r"^\d+", str(index), question, count=1)
            shuffled_lines.append(question_text)
            shuffled_lines.extend(answers) # Add every answer as new element to the list
            shuffled_lines.append("")

        return shuffled_lines


# =============================================================================================
def get_local_ip():
    """Get the local IP address of the machine running the server."""
    try:
        # Create a UDP socket to get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) # Connect to a public DNS server (Google's)
        local_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        local_ip = "127.0.0.1"
        print(f"Error getting local IP address: {e}")

    return local_ip


# =============================================================================================
def run():
    """Start the server."""
    server_address = ('', consts.server_port)
    httpd = HTTPServer(server_address, ExamHandler)

    print(f"Server socket: {get_local_ip()}:{consts.server_port}")
    print(f"Exam name: {consts.exam_txt_file_name}")
    httpd.serve_forever()


if __name__ == '__main__':
    run()