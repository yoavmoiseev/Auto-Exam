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
    def is_russian_text(text):
        """Check if text contains Russian/Cyrillic characters"""
        for char in text:
            if "\u0400" <= char <= "\u04FF":  # Cyrillic Unicode range
                return True
        return False
    
    @staticmethod
    def detect_language(text):
        """
        Detect language of text
        Priority: Hebrew > Russian > English
        If any Hebrew or Russian found, it's NOT English
        """
        if ExamBuilder.is_hebrew_text(text):
            return 'he'
        elif ExamBuilder.is_russian_text(text):
            return 'ru'
        else:
            return 'en'
    
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
    
    @staticmethod
    def parse_exam_file_for_preview(filepath, shuffle=True):
        """
        Parse exam file and return questions for preview
        Same logic as for students but with shuffle option
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return ExamBuilder.parse_exam_content(content, shuffle)
        except Exception as e:
            raise Exception(f"Failed to parse exam file: {str(e)}")
    
    @staticmethod
    def parse_exam_content(content, shuffle=True):
        """
        Parse exam content string and return questions
        Uses the SAME logic as original Exam.py
        """
        try:
            lines = content.split('\n')
            
            # Build question-answer dict first (original logic)
            qa_dict = {}
            current_question = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a question
                if re.match(ExamBuilder.QUESTION_PATTERN, line):
                    # Extract question text after number
                    try:
                        idx = line.index(ExamBuilder.START_OF_QUESTION_MARK)
                        current_question = line[idx + 1:].strip()
                    except ValueError:
                        current_question = line
                # If we have current question and it's not in dict yet, this is first answer
                elif current_question and current_question not in qa_dict:
                    qa_dict[current_question] = line
            
            # Now parse all questions with their answers
            questions = []
            current_question_line = ""
            current_answers = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this is a question line
                if re.match(ExamBuilder.QUESTION_PATTERN, line):
                    # Save previous question if exists
                    if current_question_line and current_answers:
                        questions.append(ExamBuilder._build_question_obj(
                            current_question_line, current_answers, qa_dict
                        ))
                    
                    # Start new question
                    current_question_line = line
                    current_answers = []
                else:
                    # This is an answer line
                    current_answers.append(line)
            
            # Add last question
            if current_question_line and current_answers:
                questions.append(ExamBuilder._build_question_obj(
                    current_question_line, current_answers, qa_dict
                ))
            
            # Shuffle if needed
            if shuffle:
                questions = ExamBuilder.shuffle_exam(questions, True)
            else:
                # Just renumber without shuffling
                for idx, q in enumerate(questions, 1):
                    q['number'] = idx
            
            return questions
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to parse exam content: {str(e)}")
    
    @staticmethod
    def _build_question_obj(question_line, answers, qa_dict):
        """
        Build question object from question line and answers
        Same logic as original Exam._build_question_html
        """
        # Get question text without number
        question_text = ExamBuilder.remove_number(question_line)
        
        # Determine question type
        q_type = 'multiple_choice'
        if question_text in qa_dict:
            first_answer = qa_dict[question_text]
            if ExamBuilder.is_open_question_marker(first_answer):
                q_type = 'open'
        
        # Build question object
        question_obj = {
            'number': 0,  # Will be set later
            'text': question_text,
            'full_text': question_line,  # Keep full text with number
            'type': q_type,
            'options': [],
            'correct_answer': qa_dict.get(question_text, None)
        }
        
        # Add options (all answer lines except open question markers)
        if q_type == 'multiple_choice':
            for answer in answers:
                # Skip answer: lines
                if answer.lower().startswith('answer:'):
                    continue
                # Skip open question markers
                if not ExamBuilder.is_open_question_marker(answer):
                    question_obj['options'].append(answer)
        else:
            # For open questions, keep any additional info (like "Programming task:")
            for answer in answers:
                if ExamBuilder.is_open_question_marker(answer):
                    question_obj['options'].append(answer)  # Keep the marker text
        
        return question_obj
    
    @staticmethod
    def extract_options(question_line, all_lines):
        """Extract answer options for a multiple choice question"""
        options = []
        try:
            q_index = all_lines.index(question_line)
            option_pattern = r'^[A-Za-z]\).*'
            
            for i in range(q_index + 1, len(all_lines)):
                line = all_lines[i]
                
                # Stop if we hit next question or answer line
                if re.match(ExamBuilder.QUESTION_PATTERN, line):
                    break
                if line.lower().startswith('answer:'):
                    break
                if ExamBuilder.is_open_question_marker(line):
                    break
                
                # Check if it's an option
                if re.match(option_pattern, line):
                    options.append(line)
        except Exception as e:
            print(f"Error extracting options: {e}")
        
        return options
    
    @staticmethod
    def format_exam_lines(lines):
        """Format exam lines - add open question markers where needed"""
        formatted = []
        i = 0
        while i < len(lines):
            current = lines[i]
            formatted.append(current)
            
            # Check if current is a question
            if re.match(ExamBuilder.QUESTION_PATTERN, current):
                # Check next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # If next line is also a question, insert open marker
                    if re.match(ExamBuilder.QUESTION_PATTERN, next_line):
                        formatted.append(ExamBuilder.OPEN_EXAM_MARKERS[0])
                else:
                    # Last question with no answer
                    formatted.append(ExamBuilder.OPEN_EXAM_MARKERS[0])
            
            i += 1
        
        return formatted
    
    @staticmethod
    def validate_exam_file(filepath):
        """
        Validate exam file and return metadata with errors
        Returns full text of problematic questions
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return ExamBuilder.validate_exam_content(content)
        except Exception as e:
            return {
                'valid': False,
                'errors': [{
                    'type': 'critical',
                    'message': f'Cannot read file: {str(e)}',
                    'text': ''
                }]
            }
    
    @staticmethod
    def validate_exam_content(content):
        """
        Validate exam content and return metadata with errors
        Shows full text of problematic questions
        """
        metadata = {
            'language': 'en',
            'total_questions': 0,
            'multiple_choice_count': 0,
            'open_questions_count': 0,
            'exam_type': 'Unknown',
            'valid': True,
            'errors': []
        }
        
        try:
            # Detect language
            metadata['language'] = ExamBuilder.detect_language(content)
            
            lines = content.split('\n')
            
            # Build QA dict
            qa_dict = {}
            current_question = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if re.match(ExamBuilder.QUESTION_PATTERN, line):
                    try:
                        idx = line.index(ExamBuilder.START_OF_QUESTION_MARK)
                        current_question = line[idx + 1:].strip()
                    except ValueError:
                        current_question = line
                elif current_question and current_question not in qa_dict:
                    qa_dict[current_question] = line
            
            # Extract raw question blocks for error reporting
            question_blocks = ExamBuilder.extract_question_blocks(content)
            
            # Parse all questions
            current_question_line = ""
            current_answers = []
            question_num = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if re.match(ExamBuilder.QUESTION_PATTERN, line):
                    # Validate previous question if exists
                    if current_question_line and current_answers:
                        question_num += 1
                        metadata['total_questions'] += 1
                        ExamBuilder._validate_question(
                            question_num, current_question_line, current_answers,
                            qa_dict, question_blocks, metadata
                        )
                    
                    current_question_line = line
                    current_answers = []
                else:
                    current_answers.append(line)
            
            # Validate last question
            if current_question_line and current_answers:
                question_num += 1
                metadata['total_questions'] += 1
                ExamBuilder._validate_question(
                    question_num, current_question_line, current_answers,
                    qa_dict, question_blocks, metadata
                )
            
            # Determine exam type
            if metadata['multiple_choice_count'] > 0 and metadata['open_questions_count'] > 0:
                metadata['exam_type'] = 'Mixed'
            elif metadata['multiple_choice_count'] > 0:
                metadata['exam_type'] = 'Multiple Choice'
            elif metadata['open_questions_count'] > 0:
                metadata['exam_type'] = 'Open Questions'
            
            metadata['valid'] = len(metadata['errors']) == 0
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            metadata['valid'] = False
            metadata['errors'].append({
                'type': 'critical',
                'message': f'Parsing error: {str(e)}',
                'text': content[:500] if len(content) > 500 else content
            })
        
        return metadata
    
    @staticmethod
    def _validate_question(question_num, question_line, answers, qa_dict, question_blocks, metadata):
        """
        Validate a single question and update metadata
        """
        question_text = ExamBuilder.remove_number(question_line)
        
        # Determine type
        q_type = 'multiple_choice'
        if question_text in qa_dict:
            first_answer = qa_dict[question_text]
            if ExamBuilder.is_open_question_marker(first_answer):
                q_type = 'open'
                metadata['open_questions_count'] += 1
            else:
                metadata['multiple_choice_count'] += 1
        else:
            metadata['multiple_choice_count'] += 1
        
        # Validate multiple choice
        if q_type == 'multiple_choice':
            # Count actual options (not answer: lines)
            options = [a for a in answers if not a.lower().startswith('answer:')]
            
            # Get raw text for error reporting
            raw_text = question_blocks.get(question_num, question_line + '\n' + '\n'.join(answers))
            
            # Check for correct answer
            if question_text not in qa_dict:
                metadata['errors'].append({
                    'question_num': question_num,
                    'type': 'missing_answer',
                    'message': f'Question {question_num}: Missing correct answer',
                    'text': raw_text
                })
            
            # Check options count
            if len(options) < 2:
                metadata['errors'].append({
                    'question_num': question_num,
                    'type': 'insufficient_options',
                    'message': f'Question {question_num}: Only {len(options)} options (need at least 2)',
                    'text': raw_text
                })
    
    @staticmethod
    def extract_question_blocks(content):
        """
        Extract raw text blocks for each question (for error reporting)
        Returns dict: {question_number: raw_text_block}
        """
        blocks = {}
        lines = content.split('\n')
        current_block = []
        current_q_num = 0
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check if this is a new question
            match = re.match(r'^(\d+)\.\s', line_stripped)
            if match:
                # Save previous block
                if current_q_num > 0 and current_block:
                    blocks[current_q_num] = '\n'.join(current_block)
                
                # Start new block
                current_q_num = int(match.group(1))
                current_block = [line]
            elif current_q_num > 0:
                # Add to current block
                current_block.append(line)
                
                # Stop at next question or if we have answer line
                if line_stripped.lower().startswith('answer:'):
                    # Check if next line is a new question
                    continue
        
        # Save last block
        if current_q_num > 0 and current_block:
            blocks[current_q_num] = '\n'.join(current_block)
        
        return blocks

