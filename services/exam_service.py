"""
Exam Service
Handles exam loading, parsing questions, and grading answers
Integrates with existing Exam.py logic
"""

import os
import re
from config import app_config


class ExamService:
    """Service for exam management"""
    
    def __init__(self):
        self.exams_dir = app_config.TEACHERS_DIR
        self.question_pattern = r"^\d+\.\s.*"
    
    def load_exam_file(self, teacher_id, exam_filename):
        """Load exam file for teacher"""
        exam_path = os.path.join(
            self.exams_dir,
            f'teacher_{teacher_id}',
            'exams',
            exam_filename
        )
        
        if not os.path.exists(exam_path):
            return None
        
        try:
            with open(exam_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._parse_exam(content)
        except Exception as e:
            print(f"Error loading exam: {e}")
            return None
    
    def _parse_exam(self, content):
        """Parse exam file into questions and answers"""
        lines = content.strip().split('\n')
        questions = []
        current_question = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if line is a question (starts with number and dot)
            if re.match(self.question_pattern, line):
                # Save previous question
                if current_question:
                    questions.append(current_question)
                
                # Start new question
                current_question = {
                    'text': line,
                    'answers': []
                }
            elif current_question is not None:
                # Add answer to current question
                current_question['answers'].append(line)
        
        # Add last question
        if current_question:
            questions.append(current_question)
        
        return {
            'questions': questions,
            'total': len(questions)
        }
    
    def grade_answer(self, question, student_answer):
        """Grade student answer against correct answer"""
        if not question['answers']:
            return {'correct': False, 'message': 'No answers available'}
        
        correct_answer = question['answers'][0]  # First answer is correct
        
        # Simple exact match (can be enhanced later)
        if student_answer.strip().lower() == correct_answer.strip().lower():
            return {'correct': True, 'message': 'Correct!'}
        
        return {'correct': False, 'message': 'Incorrect'}
    
    def save_exam_results(self, teacher_id, exam_name, results):
        """Save exam results to file"""
        results_dir = os.path.join(
            self.exams_dir,
            f'teacher_{teacher_id}',
            'results'
        )
        
        os.makedirs(results_dir, exist_ok=True)
        
        results_file = os.path.join(results_dir, f'GRADES_{exam_name}.txt')
        
        try:
            with open(results_file, 'a', encoding='utf-8') as f:
                f.write(results + '\n')
            return True
        except Exception as e:
            print(f"Error saving results: {e}")
            return False
