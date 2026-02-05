"""Simple build script without Russian text"""
import os
import shutil
import subprocess
import sys

print("Building Exam System Offline...")

# Clean old builds
for folder in ['dist', 'build', 'ExamSystem-Offline']:
    if os.path.exists(folder):
        shutil.rmtree(folder)
if os.path.exists('ExamSystem.spec'):
    os.remove('ExamSystem.spec')

# Create output folder
os.makedirs('ExamSystem-Offline', exist_ok=True)

# Copy files
files_to_copy = ['app.py', 'config.py', 'consts.py', 'Exam.py', 'script.js', 'requirements.txt', 'README.md']
folders_to_copy = ['data', 'templates', 'static', 'services', 'routes', 'video', 'Exams']

print("Copying files...")
for file in files_to_copy:
    if os.path.exists(file):
        shutil.copy2(file, 'ExamSystem-Offline/')
        print(f"  + {file}")

for folder in folders_to_copy:
    if os.path.exists(folder):
        dest = os.path.join('ExamSystem-Offline', folder)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(folder, dest)
        print(f"  + {folder}/")

# Create empty folders
for folder in ['teachers', 'logs']:
    os.makedirs(os.path.join('ExamSystem-Offline', folder), exist_ok=True)
    print(f"  + {folder}/ (empty)")

# Build EXE with PyInstaller
print("\nBuilding EXE (this takes 2-3 minutes)...")
pyinstaller_cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--name=ExamSystem",
    "--onedir",
    "--console",  # Show console window (not --windowed)
    "--noupx",
    "--icon=NONE",
    "--hidden-import=flask",
    "--hidden-import=flask.json",
    "--hidden-import=werkzeug",
    "--hidden-import=werkzeug.security",
    "--hidden-import=jinja2",
    "--hidden-import=jinja2.ext",
    "--hidden-import=sqlite3",
    "--hidden-import=hashlib",
    "--hidden-import=logging",
    "--collect-all=flask",
    "--collect-all=werkzeug",
    "--collect-all=jinja2",
    "--add-data=templates;templates",
    "--add-data=static;static",
    "--add-data=data;data",
    "--add-data=services;services",
    "--add-data=routes;routes",
    "--add-data=video;video",
    "--add-data=Exams;Exams",
    "start_server.py"  # Use simple CMD launcher
]

try:
    result = subprocess.run(pyinstaller_cmd, check=True, capture_output=True, text=True)
    print("PyInstaller completed successfully")
except subprocess.CalledProcessError as e:
    print(f"ERROR: PyInstaller failed with code {e.returncode}")
    print(e.stderr)
    sys.exit(1)

# Copy EXE folder to ExamSystem-Offline
print("\nCopying EXE files...")
exe_folder = os.path.join('dist', 'ExamSystem')
if os.path.exists(exe_folder):
    for item in os.listdir(exe_folder):
        src = os.path.join(exe_folder, item)
        dst = os.path.join('ExamSystem-Offline', item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    print("  EXE files copied")

# Create ZIP
print("\nCreating ZIP archive...")
shutil.make_archive('ExamSystem-Offline', 'zip', '.', 'ExamSystem-Offline')
print("  ExamSystem-Offline.zip created")

print("\n" + "="*60)
print("BUILD COMPLETE!")
print("="*60)
print(f"\nFolder: ExamSystem-Offline/")
print(f"Archive: ExamSystem-Offline.zip")
print(f"\nTo test:")
print(f"1. Open ExamSystem-Offline folder")
print(f"2. Run ExamSystem.exe")
print(f"3. Click 'Start Server' button")
print("="*60)
