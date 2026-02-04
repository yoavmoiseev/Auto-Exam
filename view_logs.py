"""
Simple script to view flask-exam logs via HTTP request
Since SSH is not available in PowerShell, we'll create a simple endpoint or use existing tools
"""
import subprocess
import sys

# Try using Windows OpenSSH client if available
def view_logs():
    try:
        # Check if OpenSSH is available
        result = subprocess.run(
            ['where', 'ssh.exe'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            ssh_path = result.stdout.strip().split('\n')[0]
            print(f"Found SSH at: {ssh_path}")
            print("\n=== Fetching logs from server ===\n")
            
            # Get last 50 lines of logs
            cmd = [
                ssh_path,
                'ubuntu@151.145.84.100',
                'sudo journalctl -u flask-exam -n 50 --no-pager'
            ]
            
            subprocess.run(cmd)
        else:
            print("SSH client not found in PATH.")
            print("\nPlease install OpenSSH client or use PuTTY to connect:")
            print("  ssh ubuntu@151.145.84.100")
            print("  sudo journalctl -u flask-exam -n 50")
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nManual steps:")
        print("1. Open PuTTY or any SSH client")
        print("2. Connect to: ubuntu@151.145.84.100")
        print("3. Run: sudo journalctl -u flask-exam -n 50")

if __name__ == '__main__':
    view_logs()
