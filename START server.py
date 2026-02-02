from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import urllib.parse
import datetime
import consts
import Exam

# Create first instance
Ex = Exam.Exam()

class ExamHandler(BaseHTTPRequestHandler):
    # =============================================================================================
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
    # =============================================================================================
    def _handle_exam_page_request(self):
        """Serve the exam page to the client."""
        self.send_response(200) # OK
        self.send_header("Content-Type", "text/html; charset=utf-8") # HTML content
        self.end_headers() # end of headers

        # shuffle the questions and answers in the exam
        shuffled_exam = Ex._shuffle_exam_lines(Ex.source_exam)

        # build the HTML form of the exam
        html_form = Ex._build_exam_html(shuffled_exam)

        try: # send the HTML form to the client
            self.wfile.write(html_form.encode('utf-8'))
        except ConnectionAbortedError:
            print(f"{self.client_address[0]} disconnected before the response was fully sent.")
    # =============================================================================================
    def _handle_favicon_request(self):
        """Handle requests for favicon.ico."""
        self.send_response(204) # No Content
        self.end_headers()
    # =============================================================================================
    def _handle_404_request(self): # page not found
        """Handle requests for unknown URLs."""
        self.send_response(404)
        self.end_headers()
    # =============================================================================================
    def do_POST(self):
        """Handle POST requests (when the exam is submitted)."""
        if self.path == '/submit':
            self._handle_exam_submission()
        # Handle refresh notification from the client
        elif self.path == '/notify-refresh':
            self._handle_refresh_notification()
        elif self.path == '/exam-started':
            self._handle_exam_started_notification()
        elif self.path == '/check_exam_file':
            """Handle requests to check the exam file."""
            # Send a simple HTTP 200 OK response
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Exam file check OK')
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
        # Get the exam duration
        minutes = form_data.get('minutes', [0])[0]
        seconds = form_data.get('seconds', [0])[0]
        exam_timer = f"{minutes}:{seconds}"
        # Get the client's IP address and NetBIOS name
        try:
            client_ip = self.client_address[0]
        except:
            print("No network connection!")
            client_ip = "127.0.0.1"

        netbios_name = Ex.get_client_netbios_name(client_ip)
       
        # Build a dictionary of the submitted question answer pairs
        submitted_answers = {
            question: answers[0]
            for question, answers in form_data.items()
            # Skip the user's details and hidden fields
            if question not in ['first_name', 'second_name', 'class', 'e-mail',\
                                  'minutes', 'seconds']
        }

        # Calculate the grade            
        grade = Ex.count_correct_answers_percent(submitted_answers)
        if grade < 0: # Open question exam
            grade = consts.open_exam_grade
        else: # Multiple choice
            grade = str(grade) + " %"
        # Build the HTML response for the user
        response_html = Ex._build_response_html(first_name, second_name, submitted_answers, grade)
        
        # Save the feedback to: folder named as the exam name + date, 
        # add student details to summary file
        Ex._save_feedback(first_name, second_name, response_html, grade,\
                             exam_timer, client_ip, netbios_name, submitted_answers)

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
    def _handle_exam_started_notification(self):
        """Handle notifications when the exam is started."""
        self.headers['Content-Length']
        # Get the current timestamp
        current_time = datetime.datetime.now().strftime("%H:%M:%S")  
        # Save the exam start time for the client IP
        client_ip = self.client_address[0]  #MUST be self or ExamHandler
        if client_ip not in Ex.cheat_counter:
            Ex.cheat_counter[client_ip] = [current_time, -1]  # Initialize with -1 refreshes and current time
            print(f"{current_time}: Exam started-   {self.client_address[0]}")

        # Send a response to acknowledge the notification
        self.send_response(200)
        self.end_headers()

    # =============================================================================================
    def _handle_refresh_notification(self):
        """Handle notifications when the page is refreshed."""
        content_length = int(self.headers['Content-Length'])
        self.rfile.read(content_length)
        # Increment cheating attempts for the client
        client_ip = self.client_address[0] # MUST be self or ExamHandler
        if client_ip in Ex.cheat_counter:
            Ex.cheat_counter[client_ip][1] += 1  # Increment the refresh count 
            if Ex.cheat_counter[client_ip][1] > 0:
                print(f"Cheat attempt from-  {self.client_address[0]} PC_Name- {Ex.get_client_netbios_name(client_ip)}")

        # Send a response to acknowledge the notification
        self.send_response(200)
        self.end_headers()
# =============================================================================================
# =============================================================================================
def run(): 
    """Start the server."""
    server_address = ('', consts.server_port)
    httpd = HTTPServer(server_address, ExamHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    run()