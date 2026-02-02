"""
Exam Session Service
Manages exam sessions, student tracking, and proctoring
"""

import uuid
from datetime import datetime
from typing import Dict, Optional


class ExamSession:
    """Represents a single running exam session"""
    
    def __init__(self, exam_id: int, teacher_id: str, exam_filename: str, exam_title: str, settings: dict = None):
        self.exam_id = exam_id
        self.teacher_id = teacher_id
        self.exam_filename = exam_filename
        self.exam_title = exam_title
        self.start_time = datetime.now()
        self.status = "running"  # running, paused, ended
        self.students = {}  # {student_session_id: student_data}
        self.settings = settings or {}  # exam settings: shuffle, max_questions, port, duration
        self.results_folder = None  # Path to results folder (created at exam start)
    
    def add_student(self, first_name: str, last_name: str):
        """Add a student to this exam session"""
        student_session_id = str(uuid.uuid4())
        
        self.students[student_session_id] = {
            'first_name': first_name,
            'last_name': last_name,
            'start_time': datetime.now(),
            'status': 'in_progress',  # in_progress, completed, abandoned
            'score': None,
            'answers': {},
            'refresh_attempts': 0,
            'cheating_attempts': 0,
            'cheating_log': [],
            'end_time': None,
            'time_spent': 0
        }
        
        return student_session_id
    
    def get_student(self, student_session_id: str) -> Optional[Dict]:
        """Get student data"""
        return self.students.get(student_session_id)
    
    def log_cheating_attempt(self, student_session_id: str, attempt_type: str, details=None):
        """Log a cheating attempt for a student"""
        if student_session_id in self.students:
            student = self.students[student_session_id]
            student['cheating_attempts'] += 1
            
            attempt_log = {
                'timestamp': datetime.now().isoformat(),
                'type': attempt_type,
                'details': details
            }
            student['cheating_log'].append(attempt_log)
    
    def submit_student_exam(self, student_session_id: str, answers: Dict, score: float):
        """Mark student exam as completed"""
        if student_session_id in self.students:
            student = self.students[student_session_id]
            student['status'] = 'completed'
            student['score'] = score
            student['answers'] = answers
            student['end_time'] = datetime.now()
            student['time_spent'] = (
                student['end_time'] - student['start_time']
            ).total_seconds()
            
            return True
        
        return False


class ExamSessionManager:
    """Manages all active exam sessions"""
    
    def __init__(self):
        self.sessions = {}  # {exam_id: ExamSession}
        self.next_exam_id = 1
    
    def start_exam(self, teacher_id: str, exam_filename: str, exam_title: str, settings: dict = None) -> int:
        """Create a new exam session"""
        exam_id = self.next_exam_id
        self.next_exam_id += 1
        
        session = ExamSession(exam_id, teacher_id, exam_filename, exam_title, settings)
        self.sessions[exam_id] = session
        
        return exam_id
    
    def get_session(self, exam_id: int) -> Optional[ExamSession]:
        """Get exam session by ID"""
        return self.sessions.get(exam_id)
    
    def add_student_to_exam(self, exam_id: int, first_name: str, last_name: str) -> Optional[str]:
        """Add student to exam session"""
        session = self.sessions.get(exam_id)
        if not session:
            return None
        
        return session.add_student(first_name, last_name)
    
    def get_student_access_url(self, exam_id: int, base_url: str = "") -> str:
        """Generate student access URL"""
        if base_url:
            return f"{base_url}/exam/{exam_id}"
        return f"/exam/{exam_id}"
    
    def get_monitor_url(self, exam_id: int, base_url: str = "") -> str:
        """Generate teacher monitor URL"""
        if base_url:
            return f"{base_url}/teacher/exam/{exam_id}/monitor"
        return f"/teacher/exam/{exam_id}/monitor"
    
    def get_all_active_sessions(self) -> Dict[int, ExamSession]:
        """Get all active exam sessions"""
        return {
            exam_id: session 
            for exam_id, session in self.sessions.items() 
            if session.status == "running"
        }
    
    def get_session_students_summary(self, exam_id: int) -> list:
        """Get summary of all students in a session"""
        session = self.sessions.get(exam_id)
        if not session:
            return []
        
        students_list = []
        for student_id, student_data in session.students.items():
            time_spent = 0
            if student_data['status'] == 'in_progress':
                time_spent = (
                    datetime.now() - student_data['start_time']
                ).total_seconds()
            else:
                time_spent = student_data['time_spent']
            
            students_list.append({
                'student_session_id': student_id,
                'name': f"{student_data['first_name']} {student_data['last_name']}",
                'first_name': student_data['first_name'],
                'last_name': student_data['last_name'],
                'start_time': student_data['start_time'].isoformat(),
                'end_time': student_data['end_time'].isoformat() if student_data['end_time'] else None,
                'status': student_data['status'],
                'score': student_data['score'],
                'refresh_attempts': student_data['refresh_attempts'],
                'cheating_attempts': student_data['cheating_attempts'],
                'time_spent': int(time_spent)
            })
        
        return students_list
    
    def end_session(self, exam_id: int) -> bool:
        """End an exam session"""
        session = self.sessions.get(exam_id)
        if session:
            session.status = "ended"
            return True
        return False
