"""
Exam System - Flask Web Application
Main entry point for the exam management system
Supports offline mode and web deployment
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, flash
from werkzeug.middleware.proxy_fix import ProxyFix
from functools import wraps
import json
import os
import zipfile
from io import BytesIO
from datetime import datetime
import time
from config import app_config
from services.auth_service import AuthService
from services.file_service import FileService
from services.exam_session_service import ExamSessionManager
from services.exam_builder_service import ExamBuilder

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(app_config)

# Configure app to work behind nginx proxy
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# Initialize services
auth_service = AuthService()
file_service = FileService()
exam_session_manager = ExamSessionManager()

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current logged in user"""
    if 'user_id' in session:
        return auth_service.get_user(session['user_id'])
    return None


def ensure_directories():
    """Ensure all necessary directories exist"""
    directories = [
        app_config.DATA_DIR,
        app_config.TEACHERS_DIR,
        app_config.LOGS_DIR,
        os.path.join(app_config.TEACHERS_DIR, 'teacher_1', 'exams'),
        os.path.join(app_config.TEACHERS_DIR, 'teacher_1', 'results'),
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# ==========================================
# ROUTES - STATIC FILES
# ==========================================

@app.route('/video/<filename>')
def serve_video(filename):
    """Serve video files"""
    video_path = os.path.join(os.path.dirname(__file__), 'video', filename)
    if os.path.exists(video_path):
        return send_file(video_path, mimetype='video/mp4')
    return "Video not found", 404


# ==========================================
# ROUTES - AUTHENTICATION
# ==========================================

@app.route('/')
def index():
    """Home page - redirect to login or dashboard"""
    if 'user_id' in session:
        return redirect(url_for('teacher_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    request_start = time.perf_counter()
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'unknown')
    accept_language = request.headers.get('Accept-Language', 'unknown')
    app.logger.info(f"Login GET/POST - Session before: {dict(session)}, Cookie: {request.cookies.get(app.config.get('SESSION_COOKIE_NAME', 'session'))}")
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            app.logger.warning(
                "Login missing fields - ip=%s user_agent=%s accept_language=%s username=%s",
                client_ip,
                user_agent,
                accept_language,
                username
            )
            flash('Username and password required', 'error')
            return render_template('login.html')
        
        result = auth_service.authenticate(username, password)
        
        if result['success']:
            session.clear()  # Clear any old session data
            session['user_id'] = result['user']['id']
            session['username'] = result['user']['username']
            session['first_name'] = result['user']['first_name']
            session['last_name'] = result['user']['last_name']
            session.permanent = True
            app.logger.info(f"Login SUCCESS - Set session: {dict(session)}")
            response = redirect(url_for('teacher_dashboard'))
            app.logger.info(f"Redirecting to dashboard, session ID: {request.cookies.get(app.config.get('SESSION_COOKIE_NAME', 'session'))}")
            app.logger.info(
                "Login success - ip=%s user_agent=%s accept_language=%s username=%s duration_ms=%.2f",
                client_ip,
                user_agent,
                accept_language,
                username,
                (time.perf_counter() - request_start) * 1000
            )
            return response
        else:
            app.logger.warning(
                "Login failed - ip=%s user_agent=%s accept_language=%s username=%s reason=%s duration_ms=%.2f",
                client_ip,
                user_agent,
                accept_language,
                username,
                result.get('message'),
                (time.perf_counter() - request_start) * 1000
            )
            flash(result['message'], 'error')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup/registration page"""
    if request.method == 'POST':
        request_start = time.perf_counter()
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'unknown')
        accept_language = request.headers.get('Accept-Language', 'unknown')
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip() or None
        agree_terms = data.get('agree_terms', False)

        app.logger.info(
            "Signup attempt - ip=%s user_agent=%s accept_language=%s username=%s terms_accepted=%s",
            client_ip,
            user_agent,
            accept_language,
            username,
            agree_terms
        )
        
        # Validation
        if not all([username, password, first_name, last_name]):
            app.logger.warning(
                "Signup validation failed - missing_fields - ip=%s username=%s",
                client_ip,
                username
            )
            return jsonify({'success': False, 'message': 'all_fields_required'})
        
        if len(username) < 3:
            app.logger.warning(
                "Signup validation failed - short_username - ip=%s username=%s",
                client_ip,
                username
            )
            return jsonify({'success': False, 'message': 'username_too_short'})
        
        if len(password) < 6:
            app.logger.warning(
                "Signup validation failed - short_password - ip=%s username=%s",
                client_ip,
                username
            )
            return jsonify({'success': False, 'message': 'password_too_short'})
        
        if password != confirm_password:
            app.logger.warning(
                "Signup validation failed - password_mismatch - ip=%s username=%s",
                client_ip,
                username
            )
            return jsonify({'success': False, 'message': 'passwords_not_match'})
        
        # Check if terms were accepted
        if not agree_terms:
            app.logger.warning(
                "Signup validation failed - terms_not_accepted - ip=%s username=%s",
                client_ip,
                username
            )
            return jsonify({'success': False, 'message': 'must_accept_terms'})
        
        # Create user
        result = auth_service.add_user(username, password, first_name, last_name, email, terms_accepted=agree_terms)
        
        if result['success']:
            app.logger.info(
                "Signup success - ip=%s username=%s duration_ms=%.2f",
                client_ip,
                username,
                (time.perf_counter() - request_start) * 1000
            )
            return jsonify({'success': True, 'message': 'account_created_successfully', 'redirect': url_for('login')})
        else:
            app.logger.warning(
                "Signup failed - ip=%s username=%s reason=%s duration_ms=%.2f",
                client_ip,
                username,
                result.get('message'),
                (time.perf_counter() - request_start) * 1000
            )
            return jsonify({'success': False, 'message': result['message']})
    
    return render_template('signup.html')


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for login (same as /login but always returns JSON)"""
    request_start = time.perf_counter()
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'unknown')
    accept_language = request.headers.get('Accept-Language', 'unknown')
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        app.logger.warning(
            "API login missing fields - ip=%s user_agent=%s accept_language=%s username=%s",
            client_ip,
            user_agent,
            accept_language,
            username
        )
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    result = auth_service.authenticate(username, password)
    
    if result['success']:
        session['user_id'] = result['user']['id']
        session['username'] = result['user']['username']
        session['first_name'] = result['user']['first_name']
        session['last_name'] = result['user']['last_name']
        app.logger.info(
            "API login success - ip=%s user_agent=%s accept_language=%s username=%s duration_ms=%.2f",
            client_ip,
            user_agent,
            accept_language,
            username,
            (time.perf_counter() - request_start) * 1000
        )
        return jsonify({'success': True, 'redirect': url_for('teacher_dashboard')})
    else:
        app.logger.warning(
            "API login failed - ip=%s user_agent=%s accept_language=%s username=%s reason=%s duration_ms=%.2f",
            client_ip,
            user_agent,
            accept_language,
            username,
            result.get('message'),
            (time.perf_counter() - request_start) * 1000
        )
        return jsonify({'success': False, 'message': result['message']}), 401


@app.route('/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('login'))


# ==========================================
# ROUTES - TEACHER DASHBOARD
# ==========================================

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    """Teacher dashboard"""
    app.logger.info(f"Dashboard access - Session: {dict(session)}, User ID in session: {session.get('user_id')}")
    user = get_current_user()
    return render_template('teacher_dashboard.html', user=user, user_id=user['id'])


@app.route('/teacher/exams')
@login_required
def teacher_exams():
    """List teacher's exams"""
    user = get_current_user()
    return render_template('teacher_exams.html', user=user, user_id=user['id'])


@app.route('/teacher/results')
@login_required
def teacher_results():
    """Teacher results page"""
    user = get_current_user()
    return render_template('teacher_results.html', user=user, user_id=user['id'])


@app.route('/api/results', methods=['GET'])
@login_required
def api_get_results():
    """Get exam result folders for current teacher"""
    try:
        user = get_current_user()
        teacher_id = f"teacher_{user['id']}"
        
        # Teacher's results directory
        teacher_results_dir = os.path.join(
            app_config.TEACHERS_DIR,
            teacher_id,
            'results'
        )
        
        results_folders = []
        
        if os.path.exists(teacher_results_dir):
            # Scan all folders in teacher's results directory
            for folder_name in os.listdir(teacher_results_dir):
                folder_path = os.path.join(teacher_results_dir, folder_name)
                
                if os.path.isdir(folder_path):
                    # Check if GRADES.txt exists (confirms it's a results folder)
                    grades_file = os.path.join(folder_path, 'GRADES.txt')
                    all_exams_file = os.path.join(folder_path, 'All_Exams.txt')
                    
                    if os.path.exists(grades_file):
                        # Parse folder name: "ExamName YYYY-MM-DD HH-MM"
                        parts = folder_name.rsplit(' ', 2)  # Split from right, max 2 splits
                        if len(parts) >= 3:
                            exam_name = ' '.join(parts[:-2])
                            exam_date = parts[-2]  # YYYY-MM-DD
                            exam_time = parts[-1]  # HH-MM
                        else:
                            exam_name = folder_name
                            exam_date = ''
                            exam_time = ''
                        
                        # Count students from GRADES.txt
                        student_count = 0
                        if os.path.exists(grades_file):
                            with open(grades_file, 'r', encoding='utf-8') as f:
                                student_count = len([line for line in f if line.strip()])
                        
                        # Get folder stats
                        html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
                        
                        results_folders.append({
                            'folder_name': folder_name,
                            'exam_name': exam_name,
                            'exam_date': exam_date,
                            'exam_time': exam_time,
                            'student_count': student_count,
                            'html_count': len(html_files),
                            'has_grades': os.path.exists(grades_file),
                            'has_all_exams': os.path.exists(all_exams_file),
                            'teacher_id': teacher_id
                        })
        
        # Sort by date/time (newest first)
        results_folders.sort(key=lambda x: f"{x.get('exam_date', '')} {x.get('exam_time', '')}", reverse=True)
        
        return jsonify({'success': True, 'folders': results_folders})
    
    except Exception as e:
        print(f"Error getting results: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/results/<folder_name>/list-files')
@login_required
def api_list_folder_files(folder_name):
    """List all files in result folder for viewing - NEW FEATURE v1
    REMARK: Previously only All_Exams.txt was viewable directly
    NOW: Returns list of all files in folder with metadata
    """
    try:
        user = get_current_user()
        teacher_id = f"teacher_{user['id']}"
        
        # Construct path to folder
        folder_path = os.path.join(
            app_config.TEACHERS_DIR,
            teacher_id,
            'results',
            folder_name
        )
        
        if not os.path.exists(folder_path):
            return jsonify({'success': False, 'message': 'Folder not found'}), 404
        
        # Get all files in folder
        files = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                
                # Determine file type
                if filename.endswith('.html'):
                    file_type = 'html'
                    icon = '📄'
                elif filename.endswith('.txt'):
                    file_type = 'txt'
                    icon = '📝'
                else:
                    file_type = 'other'
                    icon = '📎'
                
                files.append({
                    'filename': filename,
                    'type': file_type,
                    'icon': icon,
                    'size': file_size,
                    'size_formatted': f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} B"
                })
        
        # Sort files: txt files first, then html files alphabetically
        files.sort(key=lambda x: (0 if x['type'] == 'txt' else 1, x['filename']))
        
        return jsonify({
            'success': True,
            'folder_name': folder_name,
            'files': files,
            'count': len(files)
        })
    
    except Exception as e:
        print(f"Error listing folder files: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/results/<folder_name>/<filename>')
@login_required
def api_view_result_file(folder_name, filename):
    """View a result HTML or TXT file
    FIX v2: TXT files now wrapped in <pre> for proper line breaks
    REMARK: Previously all files returned as-is, causing .txt files to display in one line in browser
    """
    try:
        user = get_current_user()
        teacher_id = f"teacher_{user['id']}"
        
        # Construct path in teacher's results folder
        file_path = os.path.join(
            app_config.TEACHERS_DIR,
            teacher_id,
            'results',
            folder_name,
            filename
        )
        
        if not os.path.exists(file_path):
            return "File not found", 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # FIX v2: Wrap .txt files in <pre> tags for proper formatting
        # REMARK: Previously returned raw content, browser ignored \n line breaks
        if filename.endswith('.txt'):
            # Wrap in HTML with proper charset and pre tag
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename}</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            padding: 20px;
            background: #f5f5f5;
        }}
        pre {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.6;
        }}
        /* Mobile responsive */
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            pre {{
                padding: 15px;
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>
    <h2>{filename}</h2>
    <pre>{content}</pre>
</body>
</html>"""
            return html_content
        else:
            # HTML files and others return as-is
            return content
    
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/api/results/<folder_name>/download-zip')
@login_required
def api_download_folder_zip(folder_name):
    """Download entire exam folder as ZIP"""
    try:
        user = get_current_user()
        teacher_id = f"teacher_{user['id']}"
        
        # Construct path to folder
        folder_path = os.path.join(
            app_config.TEACHERS_DIR,
            teacher_id,
            'results',
            folder_name
        )
        
        if not os.path.exists(folder_path):
            return "Folder not found", 404
        
        # Create ZIP in memory
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the folder and add all files
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        
        memory_file.seek(0)
        
        # Generate ZIP filename
        zip_filename = f"{folder_name}.zip"
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error creating ZIP: {str(e)}", 500


@app.route('/api/results/download-all-zip')
@login_required
def api_download_all_folders_zip():
    """Download all exam folders as one big ZIP"""
    try:
        user = get_current_user()
        teacher_id = f"teacher_{user['id']}"
        
        # Construct path to results folder
        results_path = os.path.join(
            app_config.TEACHERS_DIR,
            teacher_id,
            'results'
        )
        
        if not os.path.exists(results_path):
            return "No results found", 404
        
        # Create ZIP in memory
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through all folders in results
            for root, dirs, files in os.walk(results_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create archive name relative to results folder
                    arcname = os.path.relpath(file_path, results_path)
                    zipf.write(file_path, arcname)
        
        memory_file.seek(0)
        
        # Generate ZIP filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        zip_filename = f"All_Results_{timestamp}.zip"
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error creating ZIP: {str(e)}", 500


@app.route('/api/results/<folder_name>/delete', methods=['DELETE'])
@login_required
def api_delete_result_folder(folder_name):
    """Delete a specific exam result folder"""
    try:
        user = get_current_user()
        teacher_id = f"teacher_{user['id']}"
        
        # Construct path to folder
        folder_path = os.path.join(
            app_config.TEACHERS_DIR,
            teacher_id,
            'results',
            folder_name
        )
        
        if not os.path.exists(folder_path):
            return jsonify({'success': False, 'message': 'Folder not found'}), 404
        
        # Delete the folder and all its contents
        import shutil
        shutil.rmtree(folder_path)
        
        return jsonify({'success': True, 'message': 'Folder deleted successfully'})
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/results/delete-all', methods=['DELETE'])
@login_required
def api_delete_all_result_folders():
    """Delete all exam result folders for current teacher"""
    try:
        user = get_current_user()
        teacher_id = f"teacher_{user['id']}"
        
        # Construct path to results folder
        results_path = os.path.join(
            app_config.TEACHERS_DIR,
            teacher_id,
            'results'
        )
        
        if not os.path.exists(results_path):
            return jsonify({'success': False, 'message': 'No results folder found'}), 404
        
        # Delete all subfolders in results
        import shutil
        deleted_count = 0
        
        for item in os.listdir(results_path):
            item_path = os.path.join(results_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                deleted_count += 1
        
        return jsonify({
            'success': True, 
            'message': f'Deleted {deleted_count} folders',
            'deleted_count': deleted_count
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


# ==========================================
# ROUTES - EXAM
# ==========================================

@app.route('/exams/<exam_id>')
def exam_start(exam_id):
    """Start exam for student"""
    return render_template('exam.html', exam_id=exam_id)


@app.route('/exam')
def exam_interface():
    """Exam interface for student - loads exam by name"""
    exam_name = request.args.get('name')
    if not exam_name:
        return redirect('/'), 400
    return render_template('exam.html', exam_name=exam_name)


# ==========================================
# ROUTES - EXAM SESSION MANAGEMENT (NEW)
# ==========================================

@app.route('/api/exam/check-existing-folders', methods=['POST'])
@login_required
def api_check_existing_folders():
    """Check if teacher has existing result folders for this exam"""
    try:
        data = request.json
        exam_filename = data.get('exam_filename')
        
        if not exam_filename:
            return jsonify({'success': False, 'message': 'Exam filename required'}), 400
        
        user = get_current_user()
        teacher_id = f"teacher_{user['id']}"
        exam_title = exam_filename.replace('.txt', '')
        
        # Teacher's results directory
        teacher_results_dir = os.path.join(
            app_config.TEACHERS_DIR,
            teacher_id,
            'results'
        )
        
        existing_folders = []
        
        if os.path.exists(teacher_results_dir):
            for folder_name in os.listdir(teacher_results_dir):
                folder_path = os.path.join(teacher_results_dir, folder_name)
                
                if os.path.isdir(folder_path):
                    # Check if folder starts with exam title
                    if folder_name.startswith(exam_title + ' '):
                        # Parse folder: "ExamName YYYY-MM-DD HH-MM"
                        parts = folder_name.rsplit(' ', 2)
                        if len(parts) >= 3:
                            date_part = parts[-2]  # YYYY-MM-DD
                            time_part = parts[-1]  # HH-MM
                            
                            # Count students
                            grades_file = os.path.join(folder_path, 'GRADES.txt')
                            student_count = 0
                            if os.path.exists(grades_file):
                                with open(grades_file, 'r', encoding='utf-8') as f:
                                    student_count = len([line for line in f if line.strip()])
                            
                            existing_folders.append({
                                'folder_name': folder_name,
                                'date': date_part,
                                'time': time_part.replace('-', ':'),
                                'student_count': student_count
                            })
        
        # Sort by date/time (newest first)
        existing_folders.sort(key=lambda x: f"{x['date']} {x['time']}", reverse=True)
        
        return jsonify({
            'success': True,
            'has_existing': len(existing_folders) > 0,
            'folders': existing_folders
        })
    
    except Exception as e:
        print(f"Error checking existing folders: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/exam/start-with-settings', methods=['POST'])
@login_required
def start_exam_with_settings():
    """Teacher starts exam with GUI settings (shuffle, limit, etc.)"""
    try:
        data = request.json
        exam_filename = data.get('exam_filename')
        max_questions = data.get('max_questions', 1000)
        shuffle_exam = data.get('shuffle_exam', True)
        exam_duration = data.get('exam_duration', 60)
        block_translation = data.get('block_translation', False)  # NEW v4
        fullscreen_mode = data.get('fullscreen_mode', False)      # NEW v4
        append_to_folder = data.get('append_to_folder')  # Folder name if appending
        
        user = get_current_user()
        teacher_id = f"teacher_{user['id']}"
        
        # Get exam title (filename without .txt)
        exam_title = exam_filename.replace('.txt', '')
        
        # Create new exam session with settings
        # REMARK: Previously only max_questions, shuffle_exam, exam_duration
        exam_id = exam_session_manager.start_exam(
            teacher_id=teacher_id,
            exam_filename=exam_filename,
            exam_title=exam_title,
            settings={
                'max_questions': max_questions,
                'shuffle_exam': shuffle_exam,
                'exam_duration': exam_duration,
                'block_translation': block_translation,  # NEW v4
                'fullscreen_mode': fullscreen_mode       # NEW v4
            }
        )
        
        # Handle results folder
        exam_session = exam_session_manager.get_session(exam_id)
        if exam_session:
            if append_to_folder:
                # Append to existing folder
                results_folder = os.path.join(
                    app_config.TEACHERS_DIR,
                    teacher_id,
                    'results',
                    append_to_folder
                )
                if os.path.exists(results_folder):
                    exam_session.results_folder = results_folder
                    print(f"Appending to existing folder: {results_folder}")
                else:
                    # Fallback: create new if folder doesn't exist
                    results_folder = create_exam_results_folder(teacher_id, exam_title, exam_session.exam_filename)
                    exam_session.results_folder = results_folder
            else:
                # Create new results folder
                results_folder = create_exam_results_folder(teacher_id, exam_title, exam_session.exam_filename)
                exam_session.results_folder = results_folder
        
        # Generate monitor URL
        monitor_url = url_for('exam_monitor', exam_id=exam_id)
        
        return jsonify({
            'success': True,
            'exam_id': exam_id,
            'monitor_url': monitor_url,
            'message': 'Exam started successfully'
        })
    
    except Exception as e:
        print(f"Error starting exam: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/teacher/exam/<filename>/start', methods=['POST'])
@login_required
def start_exam_session(filename):
    """Teacher starts a new exam session (fallback without settings)"""
    user = get_current_user()
    teacher_id = f"teacher_{user['id']}"
    
    # Get exam title (filename without .txt)
    exam_title = filename.replace('.txt', '')
    
    # Create new exam session
    exam_id = exam_session_manager.start_exam(
        teacher_id=teacher_id,
        exam_filename=filename,
        exam_title=exam_title
    )
    
    # Redirect teacher to monitor dashboard
    return redirect(url_for('exam_monitor', exam_id=exam_id))


@app.route('/teacher/exam/<int:exam_id>/monitor')
@login_required
def exam_monitor(exam_id):
    """Teacher monitors exam - sees student activity in real-time"""
    user = get_current_user()
    exam_session = exam_session_manager.get_session(exam_id)
    
    if not exam_session:
        return "Exam not found", 404
    
    # Generate student access URL
    student_access_url = exam_session_manager.get_student_access_url(
        exam_id,
        base_url=request.url_root.rstrip('/')
    )
    
    return render_template('exam_monitor.html',
                          exam_id=exam_id,
                          exam_title=exam_session.exam_title,
                          student_access_url=student_access_url)


@app.route('/exam/<int:exam_id>')
def student_exam_session(exam_id):
    """Student accesses exam by session ID"""
    exam_session = exam_session_manager.get_session(exam_id)
    
    if not exam_session:
        return "This exam is not available or has ended", 404
    
    # TRANSLATION FIX v1: Determine exam language from exam content
    # REMARK: Previously no language detection - used localStorage (dashboard language)
    exam_dir = os.path.join(app_config.TEACHERS_DIR, exam_session.teacher_id, 'exams')
    exam_path = os.path.join(exam_dir, exam_session.exam_filename)
    
    try:
        # FIXED v3: Always use detect_exam_language() with percentage threshold
        # Previously: Used text_direction from ExamBuilder which could be wrong
        # Now: Direct language detection from content with 5% threshold
        with open(exam_path, 'r', encoding='utf-8') as f:
            content = f.read()
        exam_language = detect_exam_language(content)  # Returns 'ru', 'en', or 'he' with 5% threshold
    except Exception as e:
        print(f"Error detecting exam language: {e}")
        exam_language = 'en'  # Fallback to English
    
    # NEW v4: Get exam settings for student page
    # REMARK: Previously no settings passed to student page
    settings = exam_session.settings or {}
    block_translation = settings.get('block_translation', False)
    fullscreen_mode = settings.get('fullscreen_mode', False)
    
    return render_template('student_exam_session.html',
                          exam_id=exam_id,
                          exam_title=exam_session.exam_title,
                          exam_language=exam_language,
                          block_translation=block_translation,
                          fullscreen_mode=fullscreen_mode)


# ==========================================
# ROUTES - API
# ==========================================

@app.route('/api/translations/<language>')
def get_translations(language):
    """Get translations for specified language"""
    if language not in app_config.SUPPORTED_LANGUAGES:
        language = app_config.DEFAULT_LANGUAGE
    
    try:
        translations_path = os.path.join(
            app_config.DATA_DIR,
            'translations',
            f'{language}.json'
        )
        with open(translations_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        return jsonify(translations)
    except Exception as e:
        print(f"Error loading translations: {e}")
        return jsonify({}), 500


def detect_exam_language(content):
    """
    Detect exam language based on content analysis with percentage threshold
    FIXED v3: Now uses percentage-based detection (same as ExamBuilder.detect_language)
    
    Previously: Used simple count comparison (1 Hebrew char could win over 1000s of Russian)
    Now: Language must have at least 5% of total characters to be detected
    
    This prevents single words/examples from changing the entire file's language.
    Example: Russian manual with Hebrew word "עברית" stays Russian, not Hebrew.
    
    Returns: 'he' for Hebrew, 'ru' for Russian, 'en' for English
    """
    if not content or len(content) == 0:
        return 'en'
    
    hebrew_count = 0
    russian_count = 0
    total_chars = len(content)
    
    for char in content:
        # Hebrew Unicode range: U+0590 to U+05FF
        if "\u0590" <= char <= "\u05FF":
            hebrew_count += 1
        # Russian Cyrillic range: U+0400 to U+04FF
        elif "\u0400" <= char <= "\u04FF":
            russian_count += 1
    
    # Calculate percentages
    hebrew_percent = (hebrew_count / total_chars) * 100
    russian_percent = (russian_count / total_chars) * 100
    
    # Threshold: at least 5% of text must be in that language
    THRESHOLD = 5.0
    
    if hebrew_percent >= THRESHOLD:
        return 'he'  # RTL язык, требует CSS dir="rtl"
    elif russian_percent >= THRESHOLD:
        return 'ru'  # LTR язык
    else:
        return 'en'  # LTR язык (по умолчанию)


@app.route('/api/exam/<exam_filename>')
def get_exam(exam_filename):
    """Get exam content with parsed questions"""
    if not exam_filename:
        return jsonify({'success': False, 'message': 'Exam not found'}), 404
    
    try:
        # Find exam file in all teacher directories
        for root, dirs, files in os.walk(app_config.TEACHERS_DIR):
            if exam_filename in files:
                filepath = os.path.join(root, exam_filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse exam questions
                questions = parse_exam_questions(content)
                
                # Detect language
                language = detect_exam_language(content)
                
                return jsonify({
                    'success': True,
                    'filename': exam_filename,
                    'questions': questions,
                    'total_questions': len(questions),
                    'language': language
                })
        
        return jsonify({'success': False, 'message': 'Exam file not found'}), 404
    except Exception as e:
        print(f"Error loading exam: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


def parse_exam_questions(content):
    """Parse exam file format and extract questions"""
    questions = []
    lines = content.strip().split('\n')
    
    current_question = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line is a question number (e.g., "1.", "2.", etc.)
        if line[0].isdigit() and ('. ' in line or '.' == line[1]):
            # Save previous question if exists
            if current_question:
                questions.append(current_question)
            
            # Parse question number and text
            parts = line.split('. ', 1)
            if len(parts) == 2:
                current_question = {
                    'id': len(questions) + 1,
                    'number': parts[0],
                    'text': parts[1],
                    'options': [],
                    'correct_answer': None
                }
        
        # Check if line is an answer option (A), B), C), D), etc.)
        elif current_question and len(line) > 2 and line[0] in 'ABCDEFGH' and line[1] == ')':
            option_letter = line[0]
            option_text = line[3:].strip()
            current_question['options'].append({
                'letter': option_letter,
                'text': option_text
            })
        
        # Check if line is the correct answer
        elif current_question and line.lower().startswith('answer:'):
            answer = line.split(':', 1)[1].strip().upper()
            current_question['correct_answer'] = answer
    
    # Don't forget last question
    if current_question:
        questions.append(current_question)
    
    return questions


@app.route('/api/submit-exam', methods=['POST'])
def submit_exam():
    """Submit exam answers and calculate score"""
    try:
        data = request.json
        exam_filename = data.get('exam_filename')
        student_name = data.get('student_name')
        answers = data.get('answers', {})  # {question_id: answer_letter}
        time_spent = data.get('time_spent', 0)
        
        if not exam_filename or not student_name:
            return jsonify({'success': False, 'message': 'Missing required data'}), 400
        
        # Load exam to get correct answers
        for root, dirs, files in os.walk(app_config.TEACHERS_DIR):
            if exam_filename in files:
                filepath = os.path.join(root, exam_filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                questions = parse_exam_questions(content)
                
                # Calculate score
                correct = 0
                total = len(questions)
                
                for q in questions:
                    q_id = str(q['id'])
                    if q_id in answers:
                        if answers[q_id].upper() == q['correct_answer']:
                            correct += 1
                
                score = (correct / total * 100) if total > 0 else 0
                
                # Save results
                result = {
                    'student_name': student_name,
                    'exam_filename': exam_filename,
                    'correct_answers': correct,
                    'total_questions': total,
                    'score': round(score, 2),
                    'time_spent': time_spent,
                    'timestamp': datetime.now().isoformat(),
                    'answers': answers
                }
                
                # Save to results file
                results_dir = os.path.join(app_config.DATA_DIR, 'results')
                os.makedirs(results_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                result_filename = f"{student_name['first']}_{student_name['last']}_{timestamp}.json"
                result_path = os.path.join(results_dir, result_filename)
                
                with open(result_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                return jsonify({
                    'success': True,
                    'score': score,
                    'correct': correct,
                    'total': total,
                    'message': f'Exam submitted: {correct}/{total} correct'
                })
        
        return jsonify({'success': False, 'message': 'Exam file not found'}), 404
    
    except Exception as e:
        print(f"Error submitting exam: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/current-user')
def api_current_user():
    """Get current logged in user"""
    user = get_current_user()
    if user:
        return jsonify({'success': True, 'user': user})
    return jsonify({'success': False}), 401


@app.route('/api/upload-exam', methods=['POST'])
@login_required
def upload_exam():
    """Upload a new exam file"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not file.filename.endswith('.txt'):
        return jsonify({'success': False, 'message': 'Only .txt files allowed'}), 400
    
    try:
        # Keep original filename but remove path traversal attempts
        filename = file.filename
        # Remove path separators and null bytes
        filename = filename.replace('\\', '').replace('/', '').replace('\0', '')
        
        # Ensure teacher exam directory exists
        teacher_id = f"teacher_{session['user_id']}"
        exam_dir = os.path.join(app_config.TEACHERS_DIR, teacher_id, 'exams')
        os.makedirs(exam_dir, exist_ok=True)
        
        filepath = os.path.join(exam_dir, filename)
        
        # Check if file already exists
        if os.path.exists(filepath):
            return jsonify({
                'success': False,
                'message': f'File already exists: {filename}',
                'file_exists': True,
                'filename': filename
            }), 409  # 409 Conflict
        
        # Save file
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Exam uploaded',
            'filename': filename
        })
    except Exception as e:
        print(f"Error uploading exam: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/exams-list', methods=['GET'])
@login_required
def get_exams():
    """Get list of exams for current teacher"""
    try:
        teacher_id = f"teacher_{session['user_id']}"
        exam_dir = os.path.join(app_config.TEACHERS_DIR, teacher_id, 'exams')
        
        if not os.path.exists(exam_dir):
            return jsonify({'success': True, 'exams': []})
        
        exams = [f for f in os.listdir(exam_dir) if f.endswith('.txt')]
        return jsonify({'success': True, 'exams': exams})
    except Exception as e:
        print(f"Error getting exams: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/delete-exam/<filename>', methods=['DELETE'])
@login_required
def delete_exam(filename):
    """Delete an exam file"""
    try:
        # Remove path traversal attempts but keep unicode characters
        filename = filename.replace('\\', '').replace('/', '').replace('\0', '').replace('..', '')
        teacher_id = f"teacher_{session['user_id']}"
        exam_dir = os.path.join(app_config.TEACHERS_DIR, teacher_id, 'exams')
        filepath = os.path.join(exam_dir, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True, 'message': 'Exam deleted'})
        else:
            return jsonify({'success': False, 'message': 'File not found'}), 404
    except Exception as e:
        print(f"Error deleting exam: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/upload-exam/overwrite', methods=['POST'])
@login_required
def upload_exam_overwrite():
    """Upload a new exam file with overwrite confirmation"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not file.filename.endswith('.txt'):
        return jsonify({'success': False, 'message': 'Only .txt files allowed'}), 400
    
    try:
        # Keep original filename but remove path traversal attempts
        filename = file.filename
        # Remove path separators and null bytes
        filename = filename.replace('\\', '').replace('/', '').replace('\0', '')
        
        # Ensure teacher exam directory exists
        teacher_id = f"teacher_{session['user_id']}"
        exam_dir = os.path.join(app_config.TEACHERS_DIR, teacher_id, 'exams')
        os.makedirs(exam_dir, exist_ok=True)
        
        filepath = os.path.join(exam_dir, filename)
        
        # Save file (overwrite if exists)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Exam uploaded',
            'filename': filename
        })
    except Exception as e:
        print(f"Error uploading exam: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/exam-source/<filename>', methods=['GET', 'PUT'])
@login_required
def get_exam_source(filename):
    """Get or update raw source of exam file"""
    try:
        filename = filename.replace('\\', '').replace('/', '').replace('\0', '').replace('..', '')
        teacher_id = f"teacher_{session['user_id']}"
        exam_dir = os.path.join(app_config.TEACHERS_DIR, teacher_id, 'exams')
        filepath = os.path.join(exam_dir, filename)
        
        if request.method == 'GET':
            # Get exam source
            if not os.path.exists(filepath):
                return jsonify({'success': False, 'message': 'File not found'}), 404
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Detect language
            from services.exam_builder_service import ExamBuilder
            language = ExamBuilder.detect_language(content)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'content': content,
                'language': language
            })
        
        elif request.method == 'PUT':
            # Save exam source
            data = request.get_json()
            if not data or 'content' not in data:
                return jsonify({'success': False, 'message': 'No content provided'}), 400
            
            new_content = data['content']
            
            # Backup original file
            import shutil
            if os.path.exists(filepath):
                backup_path = filepath + '.backup'
                shutil.copy2(filepath, backup_path)
            
            # Save new content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Exam file updated: {filename} by teacher_{session['user_id']}")
            
            return jsonify({
                'success': True,
                'message': 'Exam saved successfully',
                'filename': filename
            })
            
    except Exception as e:
        print(f"Error with exam source: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/exam-preview/<filename>', methods=['GET'])
@login_required
def get_exam_preview(filename):
    """Get student preview of exam (no shuffle)"""
    try:
        from services.exam_builder_service import ExamBuilder
        
        filename = filename.replace('\\', '').replace('/', '').replace('\0', '').replace('..', '')
        teacher_id = f"teacher_{session['user_id']}"
        exam_dir = os.path.join(app_config.TEACHERS_DIR, teacher_id, 'exams')
        filepath = os.path.join(exam_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse exam without shuffling
        questions = ExamBuilder.parse_exam_file_for_preview(filepath, shuffle=False)
        language = ExamBuilder.detect_language(content)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'language': language,
            'questions': questions
        })
    except Exception as e:
        print(f"Error previewing exam: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/exam-data/<filename>', methods=['GET'])
@login_required
def get_exam_data(filename):
    """Get exam metadata and validation errors"""
    try:
        from services.exam_builder_service import ExamBuilder
        
        filename = filename.replace('\\', '').replace('/', '').replace('\0', '').replace('..', '')
        teacher_id = f"teacher_{session['user_id']}"
        exam_dir = os.path.join(app_config.TEACHERS_DIR, teacher_id, 'exams')
        filepath = os.path.join(exam_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        # Validate exam and get metadata
        metadata = ExamBuilder.validate_exam_file(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'metadata': metadata
        })
    except Exception as e:
        print(f"Error getting exam data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/exam-validate-content', methods=['POST'])
@login_required
def validate_exam_content():
    """Validate exam content from text (before upload)"""
    try:
        from services.exam_builder_service import ExamBuilder
        
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'success': False, 'message': 'No content provided'}), 400
        
        # Validate content
        metadata = ExamBuilder.validate_exam_content(content)
        
        return jsonify({
            'success': True,
            'metadata': metadata
        })
    except Exception as e:
        print(f"Error validating exam content: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/exam-preview-content', methods=['POST'])
@login_required
def preview_exam_content():
    """Preview exam content from text (before upload)"""
    try:
        from services.exam_builder_service import ExamBuilder
        
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'success': False, 'message': 'No content provided'}), 400
        
        # Parse and preview content
        questions = ExamBuilder.parse_exam_content(content, shuffle=False)
        language = ExamBuilder.detect_language(content)
        
        return jsonify({
            'success': True,
            'language': language,
            'questions': questions
        })
    except Exception as e:
        print(f"Error previewing exam content: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/examples-list', methods=['GET'])
@login_required
def get_examples_list():
    """Get list of example exams from Exams/ folder"""
    try:
        examples_dir = os.path.join(app_config.BASE_DIR, 'Exams')
        
        if not os.path.exists(examples_dir):
            return jsonify({'success': True, 'examples': []})
        
        examples = [f for f in os.listdir(examples_dir) if f.endswith('.txt')]
        examples.sort()
        
        return jsonify({
            'success': True,
            'examples': examples
        })
    except Exception as e:
        print(f"Error getting examples list: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/copy-example', methods=['POST'])
@login_required
def copy_example():
    """Copy example exam to teacher's exams folder"""
    try:
        import shutil
        
        data = request.get_json()
        filename = data.get('filename', '')
        
        if not filename:
            return jsonify({'success': False, 'message': 'No filename provided'}), 400
        
        # Security: sanitize filename
        filename = filename.replace('\\', '').replace('/', '').replace('\0', '').replace('..', '')
        
        examples_dir = os.path.join(app_config.BASE_DIR, 'Exams')
        source_path = os.path.join(examples_dir, filename)
        
        if not os.path.exists(source_path):
            return jsonify({'success': False, 'message': 'Example file not found'}), 404
        
        # Copy to teacher's exams folder
        teacher_id = f"teacher_{session['user_id']}"
        exam_dir = os.path.join(app_config.TEACHERS_DIR, teacher_id, 'exams')
        os.makedirs(exam_dir, exist_ok=True)
        
        dest_path = os.path.join(exam_dir, filename)
        
        # Check if file already exists
        if os.path.exists(dest_path):
            return jsonify({
                'success': False,
                'message': 'File already exists in your exams',
                'exists': True
            }), 400
        
        shutil.copy2(source_path, dest_path)
        
        return jsonify({
            'success': True,
            'message': 'Example exam copied successfully',
            'filename': filename
        })
    except Exception as e:
        print(f"Error copying example: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/exam-source-from-examples/<filename>', methods=['GET'])
@login_required
def get_exam_source_from_examples(filename):
    """Get exam source content from Examples folder"""
    try:
        from services.exam_builder_service import ExamBuilder
        
        # Security: sanitize filename
        filename = filename.replace('\\', '').replace('/', '').replace('\0', '').replace('..', '')
        
        examples_dir = os.path.join(app_config.BASE_DIR, 'Exams')
        filepath = os.path.join(examples_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Example file not found'}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        language = ExamBuilder.detect_language(content)
        
        return jsonify({
            'success': True,
            'content': content,
            'language': language
        })
    except Exception as e:
        print(f"Error reading example exam: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ==========================================
# ROUTES - API - EXAM SESSION (NEW)
# ==========================================

@app.route('/api/exam/<int:exam_id>/start-student', methods=['POST'])
def api_start_student(exam_id):
    """Student submits name and starts exam"""
    try:
        data = request.json
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        if not first_name or not last_name:
            return jsonify({'success': False, 'message': 'Name is required'}), 400
        
        # Get exam session
        exam_session = exam_session_manager.get_session(exam_id)
        if not exam_session:
            return jsonify({'success': False, 'message': 'Exam not found'}), 404
        
        # Add student to session
        student_session_id = exam_session_manager.add_student_to_exam(
            exam_id, first_name, last_name
        )
        
        # Get exam settings
        settings = getattr(exam_session, 'settings', {})
        max_questions = settings.get('max_questions', 1000)
        shuffle = settings.get('shuffle_exam', False)
        
        # Load exam questions with settings
        teacher_id = exam_session.teacher_id
        exam_data = load_exam_questions(
            teacher_id, 
            exam_session.exam_filename,
            max_questions=max_questions,
            shuffle=shuffle
        )
        
        return jsonify({
            'success': True,
            'student_session_id': student_session_id,
            'exam_data': exam_data
        })
    
    except Exception as e:
        print(f"Error starting student exam: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/exam/<int:exam_id>/questions', methods=['GET'])
def api_get_exam_questions(exam_id):
    """Get exam questions for display"""
    try:
        exam_session = exam_session_manager.get_session(exam_id)
        if not exam_session:
            return jsonify({'success': False, 'message': 'Exam not found'}), 404
        
        # Get exam settings
        settings = getattr(exam_session, 'settings', {})
        max_questions = settings.get('max_questions', 1000)
        shuffle = settings.get('shuffle_exam', False)
        
        # Load exam questions using ExamBuilder
        exam_data = load_exam_questions(
            exam_session.teacher_id,
            exam_session.exam_filename,
            max_questions=max_questions,
            shuffle=shuffle
        )
        
        questions = exam_data.get('questions', []) if isinstance(exam_data, dict) else []
        text_direction = exam_data.get('text_direction', 'ltr') if isinstance(exam_data, dict) else 'ltr'
        
        return jsonify({
            'success': True,
            'questions': questions,
            'text_direction': text_direction
        })
    
    except Exception as e:
        print(f"Error loading questions: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/exam/<int:exam_id>/submit', methods=['POST'])
def api_submit_exam(exam_id):
    """Student submits exam answers"""
    try:
        data = request.json
        student_session_id = data.get('student_session_id')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        answers = data.get('answers', {})
        questions_list = data.get('questions', [])  # Get questions student saw
        device_info = data.get('device_info', {})  # Get device fingerprint
        
        # Collect IP and User-Agent from request
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()  # Get first IP if multiple
        user_agent = request.headers.get('User-Agent', 'unknown')
        
        # Add IP and UA to device_info
        device_info['ip_address'] = client_ip
        device_info['user_agent_full'] = user_agent
        
        exam_session = exam_session_manager.get_session(exam_id)
        if not exam_session:
            return jsonify({'success': False, 'message': 'Exam not found'}), 404
        
        student = exam_session.get_student(student_session_id)
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404
        
        # Load full exam file for answer dictionary
        exam_dir = os.path.join(app_config.TEACHERS_DIR, exam_session.teacher_id, 'exams')
        exam_path = os.path.join(exam_dir, exam_session.exam_filename)
        
        full_exam_data = ExamBuilder.parse_exam_file(exam_path)
        question_answer_dict = full_exam_data.get('question_answer_dict', {})
        text_direction = full_exam_data.get('text_direction', 'ltr')
        
        # TRANSLATION FIX v3: Load translations for results page based on exam language
        # FIXED v3: Always use detect_exam_language() with percentage threshold
        # REMARK: Previously results were hard-coded in English, then used text_direction which could be wrong
        # NOW: Direct language detection from content with 5% threshold
        with open(exam_path, 'r', encoding='utf-8') as f:
            content = f.read()
        exam_language = detect_exam_language(content)  # Returns 'ru', 'en', or 'he' with 5% threshold
        
        # Load translations
        translations_path = os.path.join(app_config.DATA_DIR, 'translations', f'{exam_language}.json')
        try:
            with open(translations_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)
        except Exception as e:
            print(f"Error loading translations: {e}")
            # Fallback to English hard-coded text
            translations = {
                'exam_submitted_successfully': 'your exam was submitted successfully',
                'your_answers': 'Your Answers:',
                'your_grade_is': 'Your grade is'
            }
        
        # Calculate score using ExamBuilder logic
        score = ExamBuilder.calculate_score(answers, question_answer_dict)
        
        # Build response HTML using questions student actually saw
        # TRANSLATION FIX v3: Improved RTL support - use div instead of html tag
        # REMARK: Previously used <html dir='rtl'> which didn't apply properly inside results-content div
        if text_direction == 'rtl':
            dir_attr = 'dir="rtl" style="text-align: right; direction: rtl;"'
        else:
            dir_attr = 'style="text-align: left;"'
        
        response_html = f"<div {dir_attr}>"
        response_html += f"<h2>{first_name} {last_name}, {translations.get('exam_submitted_successfully', 'your exam was submitted successfully')}</h2>"
        response_html += f"<h3>{translations.get('your_answers', 'Your Answers:')}</h3><ol>"
        
        # Loop through questions student saw (from client) in order
        for question in questions_list:
            question_text = question.get('text', '')
            
            # Find submitted answer for this question
            submitted_answer = answers.get(question_text, 'No answer')
            
            # If exam is RTL (Hebrew), keep answers RTL too
            # Otherwise, check if answer contains English and apply LTR
            if text_direction == 'rtl':
                align_dir = ""
            else:
                is_english = any(ord('A') <= ord(char) <= ord('z') for char in submitted_answer)
                align_dir = "align='left' dir='ltr'" if is_english else ""
            
            response_html += f"<li><b>{question_text}</b><pre {align_dir}>{submitted_answer}</pre></li>"
        
        # Add grade
        # TRANSLATION FIX v2: Use translated "Your grade is" text
        # REMARK: Previously "Your grade is" was hard-coded in English
        if score < 0:
            grade_text = translations.get('open_exam_grade_pending', 'Unknown yet, exam will be evaluated later')
        else:
            grade_text = f"{score} %"
        
        # TRANSLATION FIX v3: Close div instead of html/body tags
        # REMARK: Previously closed with </body></html>
        response_html += f"<h1>{translations.get('your_grade_is', 'Your grade is')} {grade_text}</h1></ol></div>"
        
        # Mark exam as completed
        exam_session.submit_student_exam(student_session_id, answers, score)
        
        # Save results to files (HTML, GRADES.txt, All_Exams.txt)
        save_exam_results(exam_id, exam_session, student_session_id, student, score, answers, response_html, questions_list, device_info)
        
        return jsonify({
            'success': True,
            'score': score,
            'response_html': response_html,
            'message': f'Exam submitted successfully'
        })
    
    except Exception as e:
        print(f"Error submitting exam: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/exam/<int:exam_id>/log-cheating', methods=['POST'])
def api_log_cheating_attempt(exam_id):
    """Log cheating attempt for a student"""
    try:
        data = request.json
        student_session_id = data.get('student_session_id')
        attempt_type = data.get('attempt_type')
        details = data.get('details')
        
        exam_session = exam_session_manager.get_session(exam_id)
        if not exam_session:
            return jsonify({'success': False}), 404
        
        # Log the cheating attempt
        exam_session.log_cheating_attempt(student_session_id, attempt_type, details)
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"Error logging cheating: {e}")
        return jsonify({'success': False}), 500


@app.route('/api/active-exams', methods=['GET'])
@login_required
def api_get_active_exams():
    """Get all active exams for current teacher"""
    try:
        user = get_current_user()
        teacher_id = f"teacher_{user['id']}"
        
        active_sessions = exam_session_manager.get_all_active_sessions()
        
        exams_list = []
        base_url = request.url_root.rstrip('/')
        
        for exam_id, exam_session in active_sessions.items():
            # Only show exams for this teacher
            if exam_session.teacher_id == teacher_id:
                students_summary = exam_session_manager.get_session_students_summary(exam_id)
                
                completed_count = sum(1 for s in students_summary if s['status'] == 'completed')
                
                exams_list.append({
                    'exam_id': exam_id,
                    'exam_title': exam_session.exam_title,
                    'exam_filename': exam_session.exam_filename,
                    'start_time': exam_session.start_time.isoformat(),
                    'status': exam_session.status,
                    'students_count': len(students_summary),
                    'completed_count': completed_count,
                    'student_url': f"{base_url}/exam/{exam_id}"
                })
        
        return jsonify({
            'success': True,
            'exams': exams_list
        })
    
    except Exception as e:
        print(f"Error getting active exams: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/exam/<int:exam_id>/end', methods=['POST'])
@login_required
def api_end_exam(exam_id):
    """Teacher ends an exam"""
    try:
        exam_session = exam_session_manager.get_session(exam_id)
        if not exam_session:
            return jsonify({'success': False, 'message': 'Exam not found'}), 404
        
        # Verify teacher owns this exam
        user = get_current_user()
        teacher_id = f"teacher_{user['id']}"
        
        if exam_session.teacher_id != teacher_id:
            return jsonify({'success': False, 'message': 'Not authorized'}), 403
        
        # End the exam
        exam_session.status = 'ended'
        
        return jsonify({
            'success': True,
            'message': 'Exam ended successfully'
        })
    
    except Exception as e:
        print(f"Error ending exam: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    
    except Exception as e:
        print(f"Error logging cheating: {e}")
        return jsonify({'success': False}), 500


@app.route('/api/exam/<int:exam_id>/log-event', methods=['POST'])
def api_log_event(exam_id):
    """Log a general event for a student"""
    try:
        data = request.json
        student_session_id = data.get('student_session_id')
        event_type = data.get('event_type')
        event_data = data.get('event_data')
        
        exam_session = exam_session_manager.get_session(exam_id)
        if not exam_session:
            return jsonify({'success': False}), 404
        
        # Log event (could be stored in a log file)
        student = exam_session.get_student(student_session_id)
        if student:
            print(f"[EVENT] {event_type} - {student['first_name']} {student['last_name']}")
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"Error logging event: {e}")
        return jsonify({'success': False}), 500


@app.route('/api/exam/<int:exam_id>/students', methods=['GET'])
def api_get_exam_students(exam_id):
    """Get all students in exam with their current status"""
    try:
        exam_session = exam_session_manager.get_session(exam_id)
        if not exam_session:
            return jsonify({'success': False, 'message': 'Exam not found'}), 404
        
        students = exam_session_manager.get_session_students_summary(exam_id)
        
        return jsonify({
            'success': True,
            'exam_id': exam_id,
            'exam_title': exam_session.exam_title,
            'students': students
        })
    
    except Exception as e:
        print(f"Error getting students: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ==========================================
# HELPER FUNCTIONS - EXAM LOGIC
# ==========================================

def create_exam_results_folder(teacher_id, exam_title, exam_filename=None):
    """Create results folder for exam at start. Returns folder path."""
    try:
        from datetime import datetime as dt
        import shutil
        
        # Format: "ExamName YYYY-MM-DD HH-MM"
        current_datetime = dt.now().strftime("%Y-%m-%d %H-%M")
        folder_name = f"{exam_title} {current_datetime}"
        
        # Create in teacher's results directory
        teacher_results_dir = os.path.join(
            app_config.TEACHERS_DIR,
            teacher_id,
            'results'
        )
        os.makedirs(teacher_results_dir, exist_ok=True)
        
        results_folder = os.path.join(teacher_results_dir, folder_name)
        os.makedirs(results_folder, exist_ok=True)
        
        # Copy exam file to results folder
        if exam_filename:
            exam_source_path = os.path.join(
                app_config.TEACHERS_DIR,
                teacher_id,
                'exams',
                exam_filename
            )
            if os.path.exists(exam_source_path):
                exam_dest_path = os.path.join(results_folder, exam_filename)
                shutil.copy2(exam_source_path, exam_dest_path)
                print(f"Copied exam file to results: {exam_filename}")
        
        print(f"Created results folder: {results_folder}")
        return results_folder
    
    except Exception as e:
        print(f"Error creating results folder: {e}")
        # Fallback to old system
        from datetime import datetime as dt
        current_date = dt.now().strftime("%Y-%m-%d")
        results_folder = os.path.join(
            os.path.dirname(__file__),
            f"{exam_title} {current_date}"
        )
        os.makedirs(results_folder, exist_ok=True)
        return results_folder


def load_exam_questions(teacher_id, exam_filename, max_questions=1000, shuffle=False):
    """Load and parse exam file using ExamBuilder"""
    try:
        exam_dir = os.path.join(app_config.TEACHERS_DIR, teacher_id, 'exams')
        exam_path = os.path.join(exam_dir, exam_filename)
        
        if not os.path.exists(exam_path):
            return {'questions': []}
        
        # ПРАВИЛЬНАЯ ЛОГИКА: сначала загружаем ВСЕ вопросы, потом shuffle, потом limit
        # Load ALL questions first (no limit)
        exam_data = ExamBuilder.parse_exam_file(exam_path, max_questions=9999)
        
        # Apply shuffle FIRST if requested (shuffles ALL questions)
        if shuffle:
            exam_data['questions'] = ExamBuilder.shuffle_exam(exam_data['questions'], shuffle)
        
        # THEN limit to max_questions (takes first N from shuffled list)
        if max_questions < len(exam_data['questions']):
            exam_data['questions'] = exam_data['questions'][:max_questions]
        
        return exam_data
    
    except Exception as e:
        print(f"Error loading exam questions: {e}")
        return {'questions': [], 'text_direction': 'ltr', 'question_answer_dict': {}}


def calculate_exam_score(answers, exam_filename, teacher_id):
    """Calculate score based on answers using ExamBuilder"""
    try:
        exam_dir = os.path.join(app_config.TEACHERS_DIR, teacher_id, 'exams')
        exam_path = os.path.join(exam_dir, exam_filename)
        
        if not os.path.exists(exam_path):
            return 0
        
        # Use ExamBuilder to get question-answer dictionary
        exam_data = ExamBuilder.parse_exam_file(exam_path)
        question_answer_dict = exam_data.get('question_answer_dict', {})
        
        if not question_answer_dict:
            return 0
        
        # Calculate score using ExamBuilder
        score = ExamBuilder.calculate_score(answers, question_answer_dict)
        
        # If -1, it means there are open questions that can't be auto-graded
        if score < 0:
            return -1
        
        return score
    
    except Exception as e:
        print(f"Error calculating score: {e}")
        return 0


def simplify_user_agent(user_agent):
    """Simplify User-Agent string to 'Browser/OS' format for readability"""
    try:
        ua = user_agent.lower()
        
        # Detect browser
        if 'edg' in ua:
            browser = 'Edge'
        elif 'chrome' in ua and 'edg' not in ua:
            browser = 'Chrome'
        elif 'firefox' in ua:
            browser = 'Firefox'
        elif 'safari' in ua and 'chrome' not in ua:
            browser = 'Safari'
        elif 'opera' in ua or 'opr' in ua:
            browser = 'Opera'
        else:
            browser = 'Unknown'
        
        # Detect OS
        if 'windows nt 10' in ua:
            os_name = 'Win10'
        elif 'windows nt 11' in ua:
            os_name = 'Win11'
        elif 'windows' in ua:
            os_name = 'Windows'
        elif 'mac os x' in ua or 'macintosh' in ua:
            os_name = 'macOS'
        elif 'android' in ua:
            os_name = 'Android'
        elif 'iphone' in ua or 'ipad' in ua:
            os_name = 'iOS'
        elif 'linux' in ua:
            os_name = 'Linux'
        else:
            os_name = 'Unknown'
        
        return f"{browser}/{os_name}"
    except:
        return 'Unknown'


def save_exam_results(exam_id, exam_session, student_session_id, student, score, answers, response_html, questions_list, device_info=None):
    """Save exam results to files (like old Exam.py system)"""
    try:
        from datetime import datetime as dt
        
        # Use results folder from exam session (created at exam start)
        if hasattr(exam_session, 'results_folder') and exam_session.results_folder:
            results_folder = exam_session.results_folder
        else:
            # Fallback: create folder now (old behavior)
            teacher_id = exam_session.teacher_id
            exam_title = exam_session.exam_title
            current_date = dt.now().strftime("%Y-%m-%d")
            results_folder = os.path.join(
                os.path.dirname(__file__),
                f"{exam_title} {current_date}"
            )
            os.makedirs(results_folder, exist_ok=True)
        
        current_time = dt.now().strftime("%H-%M-%S")
        # FIX v3: Date format with year, month name, day
        # REMARK: Previously "%Y-%m-%d" (2026-02-03), now "%Y %B %d" (2026 February 03)
        current_date = dt.now().strftime("%Y %B %d")
        first_name = student['first_name']
        last_name = student['last_name']
        
        # 1. Save HTML file (student's exam result)
        html_filename = f"{first_name}_{last_name}_{current_time}.html"
        html_path = os.path.join(results_folder, html_filename)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(response_html)
        
        # 2. Append to GRADES.txt
        # FIX v3: Improved format to handle names with numbers
        # REMARK: Previously format was "HH-MM-SS: Name-Score%" which confused names with numbers
        # NEW FORMAT: "YYYY-MM-DD HH-MM-SS | FullName | Score: XX% | Cheat: X | Duration: X | IP: xxx | UA: xxx | Device: xxx | Screen: xxx"
        grades_file = os.path.join(results_folder, 'GRADES.txt')
        cheating_attempts = student.get('cheating_attempts', 0)
        
        # FIX v4: Use time_spent instead of exam_duration, format as "5m 23s"
        # REMARK: Previously used 'exam_duration' key which didn't exist (showed N/A)
        time_spent_seconds = student.get('time_spent', 0)
        if time_spent_seconds and time_spent_seconds > 0:
            minutes = int(time_spent_seconds // 60)
            seconds = int(time_spent_seconds % 60)
            exam_duration = f"{minutes}m {seconds}s"
        else:
            exam_duration = "N/A"
        
        # Extract device information for fraud detection
        if device_info:
            ip_address = device_info.get('ip_address', 'unknown')
            device_id = device_info.get('device_id', 'unknown')
            platform = device_info.get('platform', 'unknown')
            screen = device_info.get('screen_resolution', 'unknown')
            
            # Simplify User-Agent (extract browser and OS)
            user_agent = device_info.get('user_agent_full', 'unknown')
            ua_short = simplify_user_agent(user_agent)
        else:
            ip_address = 'unknown'
            device_id = 'unknown'
            ua_short = 'unknown'
            platform = 'unknown'
            screen = 'unknown'
        
        grade_text = f"{score}%" if score >= 0 else "Unknown yet"
        grades_entry = (
            f"{current_date} {current_time} | {first_name} {last_name} | "
            f"Score: {grade_text} | Cheat: {cheating_attempts} | Duration: {exam_duration} | "
            f"IP: {ip_address} | UA: {ua_short} | Device: {device_id} | Screen: {screen}\n"
        )
        
        with open(grades_file, 'a', encoding='utf-8') as f:
            f.write(grades_entry)
        
        # 3. Append to All_Exams.txt (for ChatGPT evaluation)
        all_exams_file = os.path.join(results_folder, 'All_Exams.txt')
        
        # If All_Exams.txt doesn't exist, create it and add exam content first
        if not os.path.exists(all_exams_file):
            try:
                # Get exam file content
                teacher_id = exam_session.teacher_id
                exam_filename = exam_session.exam_filename
                exam_file_path = os.path.join(
                    app_config.TEACHERS_DIR,
                    teacher_id,
                    'exams',
                    exam_filename
                )
                
                if os.path.exists(exam_file_path):
                    with open(exam_file_path, 'r', encoding='utf-8') as f:
                        exam_content = f.read()
                    
                    # Write exam content to All_Exams.txt first
                    with open(all_exams_file, 'w', encoding='utf-8') as f:
                        f.write("=" * 80 + "\n")
                        f.write("EXAM CONTENT\n")
                        f.write("=" * 80 + "\n\n")
                        f.write(exam_content)
                        f.write("\n\n")
                        f.write("=" * 80 + "\n")
                        f.write("STUDENT RESULTS\n")
                        f.write("=" * 80 + "\n\n")
                    
                    print(f"Created All_Exams.txt with exam content")
            except Exception as e:
                print(f"Error adding exam content to All_Exams.txt: {e}")
        
        # Build text format like old system + add device info
        exam_txt = "############################################################################\n\n"
        exam_txt += f"Student details: Name-{first_name}  Last name-{last_name}  "
        exam_txt += f"Submitting time-{current_time}  Cheating attemps-{cheating_attempts}\n"
        if device_info:
            exam_txt += f"Device Info: IP-{ip_address}  Device-{device_id}  Platform-{platform}  Screen-{screen}\n"
        exam_txt += "\n"
        
        # Add all questions and answers
        for question in questions_list:
            question_text = question.get('text', '')
            submitted_answer = answers.get(question_text, 'No answer')
            
            exam_txt += f"{question_text}\n{submitted_answer}\n"
            exam_txt += "\n----------------------------------------------------------------------------\n"
        
        with open(all_exams_file, 'a', encoding='utf-8') as f:
            f.write(exam_txt)
        
        print(f"Exam submitted {grades_entry}")
        
        return True
    
    except Exception as e:
        print(f"Error saving results: {e}")
        import traceback
        traceback.print_exc()
        return False


# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def page_not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    print(f"Internal server error: {error}")
    return render_template('500.html'), 500


# ==========================================
# APPLICATION INITIALIZATION
# ==========================================

@app.before_request
def before_request():
    """Before each request"""
    ensure_directories()


@app.context_processor
def inject_user():
    """Inject user into template context"""
    return dict(current_user=get_current_user())


# ==========================================
# MAIN
# ==========================================

if __name__ == '__main__':
    # Ensure all directories exist
    ensure_directories()
    
    # Create default teacher if not exists
    result = auth_service.add_user(
        username='teacher1',
        password='password123',
        first_name='Teacher',
        last_name='One',
        email='teacher1@exam-system.local'
    )
    if result['success']:
        print("✓ Default teacher account created (username: teacher1, password: password123)")
    else:
        print(f"ℹ Default teacher: {result['message']}")
    
    # Print startup info
    print("\n" + "="*60)
    print("Exam System - Flask Application")
    print("="*60)
    print(f"Database: {app_config.DATABASE_PATH}")
    print(f"Teachers Dir: {app_config.TEACHERS_DIR}")
    print(f"Logs Dir: {app_config.LOGS_DIR}")
    print(f"Debug Mode: {app_config.DEBUG}")
    print("="*60 + "\n")
    
    # Get port from environment variable or default to 5001
    # REMARK: Changed from hardcoded 5000 to support multiple deployments on same VM
    port = int(os.environ.get('FLASK_PORT', 5001))
    
    # Start Flask development server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app_config.DEBUG
    )
