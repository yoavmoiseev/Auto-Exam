"""
Offline Launcher for Exam System
Standalone version with proper server management and graceful shutdown
Based on School Scheduler approach
"""
import os
import sys
import socket
import webbrowser
import threading
import signal
import time
from werkzeug.serving import make_server

# Add current directory to path for imports
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

# Global server object
server = None
server_thread = None

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def open_browser(url):
    """Open browser after short delay"""
    time.sleep(1.5)
    try:
        webbrowser.open(url)
    except:
        pass

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n[INFO] Shutting down server...")
    if server:
        server.shutdown()
    print("[INFO] Server stopped successfully")
    sys.exit(0)

def run_server(app, host, port):
    """Run Flask server in a separate thread"""
    global server
    try:
        server = make_server(host, port, app, threaded=True)
        print(f"\n[INFO] Server running at http://{host}:{port}")
        print("[INFO] Press Ctrl+C to stop the server\n")
        server.serve_forever()
    except Exception as e:
        print(f"[ERROR] Server error: {e}")

def main():
    """Main entry point"""
    global server_thread
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("="*70)
    print(" 📚 Exam System - Offline Standalone Version")
    print("="*70)
    print()
    
    # Get IP and port
    ip_address = get_local_ip()
    port = 5000
    url = f"http://{ip_address}:{port}"
    
    print(f" 🌐 Server IP:    {ip_address}")
    print(f" 🔌 Port:         {port}")
    print(f" 🔗 Local URL:    http://localhost:{port}")
    print(f" 🔗 Network URL:  {url}")
    print()
    print("="*70)
    print(" ✅ Starting server... Please wait...")
    print("="*70)
    print()
    
    try:
        # Import Flask app
        print("[INFO] Loading application...")
        from app import app
        
        # Ensure directories exist
        print("[INFO] Ensuring directories exist...")
        from app import ensure_directories
        ensure_directories()
        
        # Disable debug mode for production
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        # Start server in a separate thread
        server_thread = threading.Thread(
            target=run_server,
            args=(app, '0.0.0.0', port),
            daemon=True
        )
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Open browser
        print("[INFO] Opening browser...")
        browser_thread = threading.Thread(target=open_browser, args=(url,))
        browser_thread.start()
        
        # Keep main thread alive
        print("\n" + "="*70)
        print(" ✅ Server is running!")
        print(" 📖 Browser should open automatically")
        print(" ⚠️  To stop: Press Ctrl+C")
        print("="*70)
        print()
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        signal_handler(None, None)
    except Exception as e:
        print(f"\n[ERROR] Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
