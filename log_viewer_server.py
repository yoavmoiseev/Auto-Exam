#!/usr/bin/env python3
"""
Simple log viewer endpoint for flask-exam service
Run this on the server to view logs via HTTP
"""
from flask import Flask, Response, jsonify
import subprocess
import sys

app = Flask(__name__)

@app.route('/view-logs')
def view_logs():
    """View last 200 lines of flask-exam logs"""
    try:
        result = subprocess.run(
            ['sudo', 'journalctl', '-u', 'flask-exam', '-n', '200', '--no-pager'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return Response(result.stdout, mimetype='text/plain')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/view-logs/yoav')
def view_yoav_logs():
    """View logs related to yoav logins"""
    try:
        result = subprocess.run(
            ['sudo', 'journalctl', '-u', 'flask-exam', '-n', '500', '--no-pager'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Filter for yoav-related lines
        lines = result.stdout.split('\n')
        filtered = [line for line in lines if 'yoav' in line.lower() or 
                   ('Session' in line and ('Login' in line or 'Dashboard' in line))]
        
        return Response('\n'.join(filtered), mimetype='text/plain')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/git-pull')
def git_pull():
    """Pull latest code from git"""
    try:
        result = subprocess.run(
            ['git', 'pull'],
            cwd='/home/ubuntu/apps/Ex',
            capture_output=True,
            text=True,
            timeout=30
        )
        return Response(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}", 
                       mimetype='text/plain')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/restart-service')
def restart_service():
    """Restart flask-exam service"""
    try:
        result = subprocess.run(
            ['sudo', 'systemctl', 'restart', 'flask-exam'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Wait a bit
        import time
        time.sleep(2)
        
        # Check status
        status = subprocess.run(
            ['sudo', 'systemctl', 'status', 'flask-exam', '--no-pager'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return Response(f"Restart result:\n{result.stdout}\n{result.stderr}\n\nStatus:\n{status.stdout}", 
                       mimetype='text/plain')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Index page with links"""
    return """
    <html>
    <head><title>Ex System Log Viewer</title></head>
    <body>
        <h1>Ex System Management</h1>
        <ul>
            <li><a href="/view-logs">View all logs (last 200 lines)</a></li>
            <li><a href="/view-logs/yoav">View yoav-related logs</a></li>
            <li><a href="/git-pull">Git pull (update code)</a></li>
            <li><a href="/restart-service">Restart flask-exam service</a></li>
        </ul>
        <p>Note: This is a temporary debug tool. Remove after debugging.</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("Starting log viewer on port 8888...")
    print("Access at: http://151.145.84.100:8888/")
    app.run(host='0.0.0.0', port=8888, debug=False)
