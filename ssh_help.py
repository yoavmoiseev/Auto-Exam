"""
Create a simple web endpoint on the server to view logs via HTTP
This script will help set up log viewing without SSH
"""
import http.server
import socketserver
import subprocess

print("""
Since SSH connection is not working from this machine, here are your options:

Option 1 - Use PuTTY (RECOMMENDED):
====================================
1. Open PuTTY
2. Connect to: ubuntu@151.145.84.100
3. Run these commands:
   cd ~/apps/Ex
   git pull
   sudo systemctl restart flask-exam
   sudo journalctl -u flask-exam -n 100 | grep -i yoav

Option 2 - Use Windows SSH Client directly:
===========================================
If you have Git Bash or WSL installed, open it and run:
   ssh ubuntu@151.145.84.100
   cd ~/apps/Ex && git pull && sudo systemctl restart flask-exam
   sudo journalctl -u flask-exam -n 100 | grep -i yoav

Option 3 - Create a log viewer on the server:
==============================================
Connect to the server and create this file ~/apps/Ex/view_logs.py:

#!/usr/bin/env python3
import subprocess
from flask import Flask, Response

app = Flask(__name__)

@app.route('/logs')
def logs():
    result = subprocess.run(
        ['sudo', 'journalctl', '-u', 'flask-exam', '-n', '200', '--no-pager'],
        capture_output=True,
        text=True
    )
    return Response(result.stdout, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)

Then run it and access: http://151.145.84.100:8888/logs

Would you like me to create instructions for any of these options?
""")
