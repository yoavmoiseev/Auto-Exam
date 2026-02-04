import subprocess
import sys

def run_ssh_command(command):
    """Run SSH command to the server"""
    ssh_cmd = f'plink -ssh ubuntu@151.145.84.100 -batch "{command}"'
    try:
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

print("=== Pulling latest code ===")
run_ssh_command("cd ~/apps/Ex && git pull")

print("\n=== Restarting flask-exam service ===")
run_ssh_command("sudo systemctl restart flask-exam")

print("\n=== Checking service status ===")
run_ssh_command("sudo systemctl status flask-exam --no-pager -n 10")

print("\n=== Recent logs ===")
run_ssh_command("sudo journalctl -u flask-exam -n 20 --no-pager")
