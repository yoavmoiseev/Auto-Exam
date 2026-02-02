"""
Exam Builder Service - based on original Exam.py
Правильная логика для парсинга и построения экзаменов
"""
import re
import random
import os


class ExamBuilder:
    """
    Service for building exams from text files
    Uses the proven logic from original Exam.py
    """
    
    # Pattern for identifying questions: "1. What is..."
    QUESTION_PATTERN = r"^\d+\.\s.*"
    START_OF_QUESTION_MARK = "."
    
    # Open question markers
    OPEN_EXAM_MARKERS = [
        "Programming task:",
        "Open Question/Multiple lines question/task:",
        "Type your answer here"
    ]
    
    def __init__(self):
        pass
    
    @staticmethod
    def is_open_question_marker(text):
        """Check if text is an open question marker"""
        return any(marker in text for marker in ExamBuilder.OPEN_EXAM_MARKERS)
    
    @staticmethod
    def is_hebrew_text(text):
        """Check if text contains Hebrew characters"""
        for char in text:
            if "\u0590" <= char <= "\u05FF":
                return True
        return False
    
    @staticmethod
    def remove_number(question):
        """Remove question number: '1. What is...' -> 'What is...'"""
        try:
            idx = question.index(ExamBuilder.START_OF_QUESTION_MARK)
            # Skip the dot and any spaces after it
            result = question[idx + 1:].strip()
            return result
        except ValueError:
            return question
    
    @staticmethod
    def remove_spaces(line):
        """Remove leading whitespaces"""
        try:
            while line and line[0] == ' ':
                line = line[1:]
        except:
            pass
        return line
    
    @staticmethod
    def format_exam(lines):
        """
        Automatically finds and marks open questions by adding specific answer marker
        Removes empty lines and handles question/answer pairs
        """
        # Remove empty lines
        lines = [line for line in lines if line.strip()]
        
        i = 0
        while i < (len(lines) - 1):
            lines[i] = ExamBuilder.remove_spaces(lines[i])
            lines[i + 1] = ExamBuilder.remove_spaces(lines[i + 1])
            
            # Two sequential questions - no answer line between them
            if (re.match(ExamBuilder.QUESTION_PATTERN, lines[i]) and
                re.match(ExamBuilder.QUESTION_PATTERN, lines[i + 1])):
                lines.insert(i + 1, ExamBuilder.OPEN_EXAM_MARKERS[0])
            i += 1
        
        # If the last question has no answer line
        if lines and re.match(ExamBuilder.QUESTION_PATTERN, lines[-1]):
            lines.append(ExamBuilder.OPEN_EXAM_MARKERS[0])
        
        return lines
    
    @staticmethod
    def build_question_answer_dict(lines):
        """
        Build a dictionary of questions and their first answers
        Returns: {question_text: first_answer}
        """
        question_answer_dict = {}
        current_question = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a question
            if re.match(ExamBuilder.QUESTION_PATTERN, line):
                # Remove the number and set as current question
                current_question = ExamBuilder.remove_number(line)
            # If we have a current question and it's not in dict yet, add first answer
            elif current_question and current_question not in question_answer_dict:
                question_answer_dict[current_question] = line
        
        return question_answer_dict
    
    @staticmethod
    def parse_exam_file(filepath, max_questions=1000):
        """
        Parse exam file and return structured data
        Returns: {
            'questions': [...],
            'text_direction': 'rtl' or 'ltr',
            'question_answer_dict': {...}
        }
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Format and clean lines
        lines = ExamBuilder.format_exam(lines)
        
        # Build answer dictionary
        question_answer_dict = ExamBuilder.build_question_answer_dict(lines)
        
        # Determine text direction
        text_direction = 'rtl' if ExamBuilder.is_hebrew_text(''.join(lines)) else 'ltr'
        
        # Build structured questions
        questions = ExamBuilder.build_questions_list(lines, question_answer_dict, max_questions)
        
        return {
            'questions': questions,
            'text_direction': text_direction,
            'question_answer_dict': question_answer_dict,
            'total_questions': len(questions)
        }
    
    @staticmethod
    def build_questions_list(lines, question_answer_dict, max_questions=1000):
        """
        Build a list of structured questions with answers
        """
        questions = []
        current_question = None
        current_answers = []
        question_counter = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a question
            if re.match(ExamBuilder.QUESTION_PATTERN, line):
                # Save previous question if exists
                if current_question and current_answers:
                    # Remove number from question text for display
                    clean_question = ExamBuilder.remove_number(current_question)
                    
                    questions.append({
                        'id': len(questions) + 1,
                        'number': question_counter,
                        'text': clean_question,  # Use cleaned version without number
                        'original_text': current_question,  # Keep original for matching
                        'answers': current_answers.copy(),
                        'type': ExamBuilder.get_question_type(clean_question, question_answer_dict),
                        'correct_answer': ExamBuilder.get_correct_answer(clean_question, question_answer_dict)
                    })
                    
                    # Check limit
                    if len(questions) >= max_questions:
                        break
                
                current_question = line
                current_answers = []
                question_counter += 1
            else:
                # It's an answer line
                current_answers.append(line)
        
        # Add last question
        if current_question and current_answers and len(questions) < max_questions:
            clean_question = ExamBuilder.remove_number(current_question)
            
            questions.append({
                'id': len(questions) + 1,
                'number': question_counter,
                'text': clean_question,  # Use cleaned version
                'original_text': current_question,  # Keep original for matching
                'answers': current_answers.copy(),
                'type': ExamBuilder.get_question_type(current_question, question_answer_dict),
                'correct_answer': ExamBuilder.get_correct_answer(current_question, question_answer_dict)
            })
        
        return questions
    
    @staticmethod
    def get_question_type(question, question_answer_dict):
        """Determine if question is 'open' or 'multiple_choice'"""
        question_key = ExamBuilder.remove_number(question)
        if question_key in question_answer_dict:
            first_answer = question_answer_dict[question_key]
            if ExamBuilder.is_open_question_marker(first_answer):
                return 'open'
        return 'multiple_choice'
    
    @staticmethod
    def get_correct_answer(question, question_answer_dict):
        """Get the correct answer for a question"""
        question_key = ExamBuilder.remove_number(question)
        if question_key in question_answer_dict:
            answer = question_answer_dict[question_key]
            if not ExamBuilder.is_open_question_marker(answer):
                return answer
        return None
    
    @staticmethod
    def shuffle_exam(questions, shuffle_enabled=True):
        """
        Shuffle questions and answers (except for open questions)
        """
        if not shuffle_enabled:
            return questions
        
        # Shuffle the questions order
        shuffled = questions.copy()
        random.shuffle(shuffled)
        
        # Shuffle answers for each multiple choice question
        for question in shuffled:
            if question['type'] == 'multiple_choice':
                # Don't shuffle the first answer if it's a marker
                if not ExamBuilder.is_open_question_marker(question['answers'][0]):
                    random.shuffle(question['answers'])
        
        # Re-number questions
        for idx, question in enumerate(shuffled, 1):
            question['number'] = idx
        
        return shuffled
    
    @staticmethod
    def calculate_score(submitted_answers, question_answer_dict):
        """
        Calculate exam score based on submitted answers
        Returns: percentage (0-100) or -1 if contains open questions
        """
        correct_count = 0
        total_questions = len(submitted_answers)
        
        for question_text, submitted_answer in submitted_answers.items():
            question_key = ExamBuilder.remove_number(question_text)
            
            if question_key in question_answer_dict:
                correct_answer = question_answer_dict[question_key]
                
                # If it's an open question, we can't auto-grade
                if ExamBuilder.is_open_question_marker(correct_answer):
                    return -1
                
                # Check if answer is correct
                if correct_answer.strip() == submitted_answer.strip():
                    correct_count += 1
        
        if total_questions == 0:
            return 0
        
        return round((correct_count / total_questions) * 100)
