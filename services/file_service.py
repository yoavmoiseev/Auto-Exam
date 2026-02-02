"""
File Service
Manages teacher exam files and results folders
"""

import os
import shutil
from config import app_config


class FileService:
    """Service for file management"""
    
    def __init__(self):
        self.teachers_dir = app_config.TEACHERS_DIR
        self.ensure_teacher_structure()
    
    def ensure_teacher_structure(self, teacher_id='teacher_1'):
        """Ensure teacher directory structure exists"""
        teacher_dir = os.path.join(self.teachers_dir, teacher_id)
        exams_dir = os.path.join(teacher_dir, 'exams')
        results_dir = os.path.join(teacher_dir, 'results')
        
        os.makedirs(exams_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)
    
    def list_exams(self, teacher_id):
        """List all exams for teacher"""
        exams_dir = os.path.join(self.teachers_dir, f'teacher_{teacher_id}', 'exams')
        
        if not os.path.exists(exams_dir):
            return []
        
        exams = []
        for filename in os.listdir(exams_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(exams_dir, filename)
                size = os.path.getsize(filepath)
                mtime = os.path.getmtime(filepath)
                
                exams.append({
                    'name': filename,
                    'size': size,
                    'modified': mtime
                })
        
        return exams
    
    def list_results(self, teacher_id):
        """List all results for teacher"""
        results_dir = os.path.join(self.teachers_dir, f'teacher_{teacher_id}', 'results')
        
        if not os.path.exists(results_dir):
            return []
        
        results = []
        for filename in os.listdir(results_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(results_dir, filename)
                size = os.path.getsize(filepath)
                mtime = os.path.getmtime(filepath)
                
                results.append({
                    'name': filename,
                    'size': size,
                    'modified': mtime
                })
        
        return results
    
    def upload_exam(self, teacher_id, file):
        """Upload exam file"""
        if not file.filename.endswith('.txt'):
            return {'success': False, 'message': 'Only .txt files allowed'}
        
        exams_dir = os.path.join(self.teachers_dir, f'teacher_{teacher_id}', 'exams')
        os.makedirs(exams_dir, exist_ok=True)
        
        try:
            filepath = os.path.join(exams_dir, file.filename)
            file.save(filepath)
            return {'success': True, 'message': 'File uploaded successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error uploading file: {str(e)}'}
    
    def delete_exam(self, teacher_id, filename):
        """Delete exam file"""
        filepath = os.path.join(self.teachers_dir, f'teacher_{teacher_id}', 'exams', filename)
        
        if not os.path.exists(filepath):
            return {'success': False, 'message': 'File not found'}
        
        try:
            os.remove(filepath)
            return {'success': True, 'message': 'File deleted'}
        except Exception as e:
            return {'success': False, 'message': f'Error deleting file: {str(e)}'}
    
    def download_results(self, teacher_id):
        """Create zip file with all results"""
        results_dir = os.path.join(self.teachers_dir, f'teacher_{teacher_id}', 'results')
        
        if not os.path.exists(results_dir):
            return None
        
        # TODO: Create zip file with results
        return results_dir
