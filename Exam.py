import socket
import os
import datetime
import random
import re
import consts

class Exam():
    # =============================================================================================
    # Global variables
    source_exam = None
    local_ip = None
    question_answer_dict = None
    exam_file_path = None
    text_direction = None
    # Counter for cheating attempts
    cheat_counter = {} # Dictionary with IP as key and number of refreshes as value
    
    # =============================================================================================
    def __init__(self):
        """The Constructor. Prepares all common data for future objects """
        # init only once
        if Exam.source_exam != None:
            return
        # Initialize exam data 
        # Read the exam file 
        Exam.source_exam = Exam._read_exam_file(Exam)
        # Adds open question addition if not entrend by file creator
        Exam.source_exam = Exam.format_exam(Exam,Exam.source_exam)

        # build the question-answer dictionary
        Exam.question_answer_dict = Exam._build_question_answer_dict\
                (self, Exam.source_exam)
        
        # verify if the current exam file is correctly formatted
        Exam._build_exam_html(Exam, Exam.source_exam)
        Exam._shuffle_exam_lines(Exam, Exam.source_exam)

        Exam.local_ip = Exam.get_local_ip()
        print(f"Server socket: {Exam.local_ip}:{consts.server_port}")
            
        curret_time= datetime.datetime.now().strftime('%H:%M:%S')
        print(f"{curret_time}:  Exam name: {consts.exam_txt_file_name}")

    # =============================================================================================
    def format_exam(self, lines):
        """
        Automaticly finds and mark open questions by adding a specific answear
        """
        try:
            while True:
                lines.remove('\n') # Removes empty lines from from lines list
        except:
            pass

        i = 0
        while i < (len(lines)-1):
            lines[i] = Exam.remove_spaces(Exam, lines[i])
            lines[i+1] = Exam.remove_spaces(Exam, lines[i+1])
            # Two sequence open questions- No between answears lines
            if re.match(consts.question_pattern, lines[i]) and\
                re.match(consts.question_pattern, lines[i+1]):
                lines.insert(i+1,consts.open_exam[0])    
            i += 1
            
        # if the last question has also NO answear line
        if re.match(consts.question_pattern, lines[-1]):
            lines.insert(len(lines),consts.open_exam[0])    

        return lines
    # =============================================================================================
    def remove_spaces(self, line):
        """remove leading whitespaces"""      
        try:
            while line[0] ==' ':
                line = line[1:]
        except:
            print("Failed to remove leadig white-spaces", line)    
        return line
    # =============================================================================================
    def is_hebrew_text(self, lines):
        """Check if the given lines contain Hebrew text."""
        for line in lines:
            for char in line:
                if "\u0590" <= char <= "\u05FF":  # Hebrew Unicode range
                    return True
        return False
    # =============================================================================================
    def set_text_direction(self, exam_content):
        """Set the text direction based on the presence of Hebrew text."""
        if Exam.is_hebrew_text(Exam, exam_content):
            Exam.text_direction = 'dir="rtl"'
        else:
            Exam.text_direction = '' # left-to-right

    # =============================================================================================
    def remove_number(self, question):
        """Remove the question number from the question string."""
        try: # remove the question number
            return question[question.index(consts.start_of_question_mark):]
        except ValueError: # if the question mark missing
            print(f"Invalid question format-  : {question}")
            return question
    # ============================================================================================
    def count_correct_answers_percent(self, submitted_answers):
        """Calculate the percentage of correct answers.
           Compares the submitted answers to the correct answers."""
        correct_answers = 0
        for question, answer in submitted_answers.items(): # check each submitted answer
            question = Exam.remove_number(Exam, question) # remove the question number
            if question in Exam.question_answer_dict:
                # An open question
                if Exam.question_answer_dict[question] in consts.open_exam:
                    return -1  # includes open questions, can NOT be checked
                # Multiple choice
                elif Exam.question_answer_dict[question] == answer:
                    correct_answers += 1
        # number of questions- minimum between examinotor setted limit
        #  and maximal number of questions in file
        total_questions = min(consts.limited_questions_number, \
                              len(Exam.question_answer_dict))
        # calculate the percentage and round it to the nearest integer
        return round((correct_answers / total_questions) * 100) 
    # =============================================================================================
    def _build_question_answer_dict(self, lines):
        """Build a dictionary of questions and their first answers."""
        question_answer_dict = {}
        current_question = None

        for line in lines: # Do NOT delete these lines
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
    def _add_exam_questions_and_answers(self, exam_content,\
                                         max_num_questions = consts.limited_questions_number):
        """Add the exam questions and answers to the HTML form."""
        html_form = ""
        current_question = ""
        answers = []
        questions_count = 0

        for line in exam_content:
            line = line.strip()  # Remove leading and trailing whitespaces
            if not line: # Skip empty lines
                continue

            # Check if the line is a question
            if re.match(consts.question_pattern, line): # check if the line is a question 
                if current_question and answers:  # If the current question has answers
                    html_form += Exam._build_question_html(Exam, current_question, answers)
                
                current_question = line
                answers = []
                questions_count += 1
                if questions_count > max_num_questions:  # Limit the number of questions
                    break
            else: # If it is an answer
                answers.append(line)

        # Add the last question and its answers
        if current_question and answers:
            html_form += Exam._build_question_html(Exam, current_question, answers)

        return html_form
    # =============================================================================================
    def _build_exam_html(self, exam_content):
        """Build the HTML form for the exam. Uses the "consts.py" file for the HTML template."""
        # Warrning page before starting the exam
        html_form = consts.html_pre_exam_page

        # Set the text direction based on the exam language
        if Exam.text_direction is None:
            Exam.set_text_direction(Exam, exam_content)
        html_form += f'<html {Exam.text_direction}>'
        # add the page/form code from the consts.py file  
        html_form += consts.html_start + consts.html_js + consts.html_middle

        # Add the exam questions and answers
        html_form += Exam._add_exam_questions_and_answers(Exam, exam_content)
        # Fit user details label to language
        html_form += consts.user_name_eng if Exam.text_direction == '' else consts.user_name_heb
        # Add the user details textboxes and submit button
        html_form += consts.user_details_textboxes + consts.submit_button
        html_form += "</form></body></html>" # End of form

        return html_form
    
    #==============================================================================================
    def _build_question_html(self, question, answers):
        """Generate the HTML code for a single question and its answers."""
        question_html = f"<fieldset><legend><b>{question}</b></legend>"

        try:
            for answer in answers:
                if Exam.question_answer_dict[Exam.remove_number(Exam, question)] \
                        in consts.open_exam: # open questions exam
                        if answer not in consts.open_exam:
                            question_html += f"<b>{answer}</b><br>"                    
                else: 
                    question_html += f"<input type='radio' name='{question}' value='{answer}'> {answer}<br>"
            
            if Exam.question_answer_dict[Exam.remove_number(Exam, question)] \
                            in consts.open_exam: # programming task
                    # add a textbox for the code
                    question_html += f"<textarea name='{question}' rows='4' cols='80'></textarea><br>"
           
        except KeyError:
            print(consts.question_format_description)
            print("Incorrect formatted question-",question)

        question_html += "</fieldset>"
        return question_html # type string

    #==============================================================================================
    def get_client_netbios_name(self, client_ip):
        """Get the NetBIOS name of the client using its IP address."""    
        try:
            netbios_name = socket.gethostbyaddr(client_ip)[0]
        except socket.herror:
            netbios_name = "Unknown"
        return netbios_name

   #=================================================================================================
    def _build_response_html(self, first_name, second_name, submitted_answers, grade):
        """Build the results HTML page for the student."""
        # F-string, allows to use variables incide the string using- {}
        response_html = f"<html {Exam.text_direction}><body><meta charset='UTF-8'>"
        response_html += f"<h2>{first_name} {second_name},\
              {consts.exam_submitted}</h2>"
        response_html += "<h3>Your Answers:</h3><ul>"
        # Build the HTML response with the submitted answers
        # Loop through the submitted answers and add them to the HTML response
        for question, answer in submitted_answers.items():
            # Adds student questions and answears to final/evaluation page
            align_dir =''
            if Exam.is_english(Exam,answer):
                align_dir = "align = 'left' dir ='ltr' " 
            response_html += f"<li><b>{question}</b>\
                <pre {align_dir} >{answer}</pre></li>"
        # Add the grade to the HTML response
        response_html += f"<h1>Your grade is {grade}</h1></ul></body></html>"
        return response_html
    #=================================================================================================
    def save_response_txt(self, first_name, second_name, submitted_answers,\
                          current_time,client_ip):
        """Build the results txt for GPT evaluation"""
        # F-string, allows to use variables incide the string using- {}
        response_txt = consts.global_delimiter
        cheating_attemps = Exam.get_cheat_counter(client_ip)
        response_txt += f"Student details: Name-{first_name}  Last name-{second_name}\
  Submitting time-{current_time}  Cheating attemps-{cheating_attemps}'\n'"
        # Loop through the submitted answers and add them to the string
        for question, answer in submitted_answers.items():
            # Adds student questions and answears
            response_txt += f"{question} '\n' {answer}"
            response_txt += consts.local_delimiter

        return response_txt
    #=================================================================================================
    def is_english(self,txt):
        for letter in txt:
            if ord('A')<= ord(letter) <= ord('z'):
                return True
        return False
    #=================================================================================================
    def get_cheat_counter(client_ip):
        try:
            # Get the number of refresh attempts for the client IP
            return Exam.cheat_counter[client_ip][1]
        except KeyError:
            # If the client IP is not in the refresh counter, set it to 0
            return 0
    #=================================================================================================
    def _format_exam_details_string(self, curr_time, first_name, second_name,\
                                     grade, exam_timer, client_ip, netbios_name):
        """Format the exam details string."""
        cheat_counter = Exam.get_cheat_counter(client_ip)

        # Convert the time strings into datetime objects
        try:
            start_time = datetime.datetime.strptime(Exam.cheat_counter[client_ip][0], "%H:%M:%S")
        except KeyError:
                        print("ERROR- NO start time")
                        start_time= datetime.datetime.now().strftime('%H:%M:%S')

        current_time = datetime.datetime.strptime(datetime.datetime.now().strftime("%H:%M:%S"), "%H:%M:%S")

        # Convert exam_timer (e.g., "10:30") into a timedelta
        minutes, seconds = map(int, exam_timer.split(":"))
        exam_duration = datetime.timedelta(minutes=minutes, seconds=seconds)

        # Calculate the time gap
        try:
            time_gap = current_time - start_time - exam_duration
            time_gap_seconds = time_gap.total_seconds()
        except:
            print("Error getting time values!")
            time_gap="0"
        return (f"{curr_time}: {first_name} {second_name}-{grade}  "
                f"Cheat Attempts-{cheat_counter} IP-{client_ip} "
                f"PC_Name-{netbios_name} Duration-{exam_timer} Time Gap-{time_gap}\n")

    #============================================================================================
    def _save_feedback(self, first_name, second_name, response_html, grade,\
                        exam_timer, client_ip, netbios_name, submitted_answers):
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

        exam_details = Exam._format_exam_details_string(Exam, current_time, first_name,\
            second_name, grade, exam_timer, client_ip, netbios_name)
        
        # File that contains the summary of all students' grades
        summary_file_path = os.path.join(folder_name, consts.grades_file_name)
        with open(summary_file_path, 'a', encoding='utf-8') as summary_file:
            summary_file.write(exam_details)

        # File that contains all students' exams in txt format
        # for chat-GPT evaluation
        current_exam = Exam.save_response_txt(Exam, first_name, second_name,\
             submitted_answers, current_time, client_ip)
        all_exams_file_path = os.path.join(folder_name, consts.all_exams_txt)
        # Append the current exam to the all_exams.txt file
        with open(all_exams_file_path, 'a', encoding='utf-8') as summary_file:
            summary_file.write(current_exam)
        
        
        # Print notification to console at exam subbmit
        print("Exam subbmited " + exam_details)


    # =============================================================================================
    def _shuffle_exam_lines(self, lines):
        """Shuffle the order of questions and answers in the exam."""
        # if shuffle exam checkbox Disabled
        if consts.shuffle_exam == False:
            return lines
        
        # Tupple (question-str, answers[list of str])
        questions = []  # ("What is 2 + 2?", ["3", "4", "5"])
        current_question = None
        current_answers = [] # List of str
        # Iterate through the lines of the exam file
        for line in lines:
            line = line.strip() # Remove leading and trailing whitespaces
            if not line: # Skip empty lines
                continue
            # Check if the line is a question, format- '1. What is a motherboard'
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
            # Do Not shuffel the answers for programming questions
            # Check if the question is a programming question
            try:
                formated_question = Exam.remove_number(self, question)                    
                if Exam.question_answer_dict\
                    [formated_question] not in consts.open_exam:
                    random.shuffle(answers) # Shuffle the answers
            except KeyError:
                print(consts.question_format_description)
                print(question)
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
    #==========================================================================================================
    def get_local_ip():
        """Get the local IP address of the machine running the server."""
        try:
            # Create a UDP socket to get the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80)) # Connect to a public DNS server (Google's)
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "127.0.0.1"
            print(f"No internet connection!")
        return local_ip
    # =========================================================================================================
