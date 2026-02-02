"""
Proctoring Service
Handles logging of student activity for cheating detection
"""

import os
import json
from datetime import datetime
from config import app_config


class ProctoringService:
    """Service for exam proctoring and logging"""
    
    def __init__(self):
        self.logs_dir = app_config.LOGS_DIR
        self.ensure_logs_dir()
    
    def ensure_logs_dir(self):
        """Ensure logs directory exists"""
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def log_exam_session(self, exam_id, student_name, student_ip, user_agent):
        """Log exam session start"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'exam_start',
            'exam_id': exam_id,
            'student_name': student_name,
            'ip_address': student_ip,
            'user_agent': user_agent
        }
        
        self._write_log(log_entry, 'exam_sessions.log')
    
    def log_cheating_attempt(self, exam_id, student_name, attempt_type, details=None):
        """Log cheating attempt"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'cheating_attempt',
            'exam_id': exam_id,
            'student_name': student_name,
            'attempt_type': attempt_type,
            'details': details or {}
        }
        
        self._write_log(log_entry, 'cheating_alerts.log')
    
    def log_exam_submission(self, exam_id, student_name, score, time_spent, cheating_attempts):
        """Log exam submission"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'exam_submit',
            'exam_id': exam_id,
            'student_name': student_name,
            'score': score,
            'time_spent': time_spent,
            'cheating_attempts': cheating_attempts
        }
        
        self._write_log(log_entry, 'exam_submissions.log')
    
    def log_login_attempt(self, username, success, ip_address=None):
        """Log login attempt"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'login_attempt',
            'username': username,
            'success': success,
            'ip_address': ip_address or 'unknown'
        }
        
        self._write_log(log_entry, 'login_history.log')
    
    def _write_log(self, entry, log_file):
        """Write log entry to file"""
        try:
            log_path = os.path.join(self.logs_dir, log_file)
            
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Error writing log: {e}")
    
    def get_exam_logs(self, log_type='all'):
        """Get logs for analysis"""
        logs = []
        
        log_files = {
            'sessions': 'exam_sessions.log',
            'cheating': 'cheating_alerts.log',
            'submissions': 'exam_submissions.log',
            'login': 'login_history.log'
        }
        
        if log_type == 'all':
            files_to_read = log_files.values()
        else:
            files_to_read = [log_files.get(log_type, 'exam_sessions.log')]
        
        for log_file in files_to_read:
            log_path = os.path.join(self.logs_dir, log_file)
            
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                logs.append(json.loads(line))
                except Exception as e:
                    print(f"Error reading log {log_file}: {e}")
        
        return logs
