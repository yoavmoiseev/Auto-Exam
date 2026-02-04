import paramiko
import sys

def check_logs():
    """Connect to server and check logs"""
    hostname = "151.145.84.100"
    username = "ubuntu"
    
    try:
        # Try to connect using SSH key
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Try common key locations
        import os
        key_paths = [
            os.path.expanduser("~/.ssh/id_rsa"),
            os.path.expanduser("~/.ssh/id_ed25519"),
            "C:/Users/User/.ssh/id_rsa",
            "C:/Users/User/.ssh/id_ed25519",
        ]
        
        connected = False
        for key_path in key_paths:
            if os.path.exists(key_path):
                try:
                    print(f"Trying key: {key_path}")
                    client.connect(hostname, username=username, key_filename=key_path, timeout=10)
                    connected = True
                    print(f"Connected using {key_path}\n")
                    break
                except Exception as e:
                    print(f"Failed with {key_path}: {e}")
                    continue
        
        if not connected:
            print("Could not connect with any SSH key")
            return
        
        # Update code
        print("=== Updating code ===")
        stdin, stdout, stderr = client.exec_command("cd ~/apps/Ex && git pull")
        print(stdout.read().decode())
        
        # Restart service
        print("\n=== Restarting service ===")
        stdin, stdout, stderr = client.exec_command("sudo systemctl restart flask-exam")
        stdout.channel.recv_exit_status()  # Wait for command to complete
        print("Service restarted")
        
        # Get logs
        print("\n=== Flask-exam logs (last 100 lines) ===")
        stdin, stdout, stderr = client.exec_command("sudo journalctl -u flask-exam -n 100 --no-pager")
        logs = stdout.read().decode()
        print(logs)
        
        # Look for yoav logins
        print("\n=== Filtering for yoav logins ===")
        for line in logs.split('\n'):
            if 'yoav' in line.lower() or 'login' in line.lower() or 'session' in line.lower():
                print(line)
        
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    try:
        import paramiko
    except ImportError:
        print("Installing paramiko...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "paramiko"], check=True)
        import paramiko
    
    check_logs()
