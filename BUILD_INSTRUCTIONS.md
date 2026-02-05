# Exam System - Standalone Offline Version
## Quick Start Guide

### Build Instructions

1. **Open PowerShell in this directory:**
   ```powershell
   cd "c:\Users\moise\OneDrive\Desktop\Ex"
   ```

2. **Run the build script:**
   ```powershell
   .\build_offline.ps1
   ```

   Or for a clean build:
   ```powershell
   .\build_offline.ps1 -Clean
   ```

3. **Wait for build to complete** (takes 2-5 minutes)

4. **Find your distribution package:**
   - Location: `ExamSystem-Offline-YYYY-MM-DD_HH-mm-ss.zip`
   - This is the file to distribute

### What Was Changed

Based on the School Scheduler repository best practices:

1. **New Launcher (`launcher_offline.py`):**
   - Proper Flask server management
   - Graceful shutdown handling (Ctrl+C)
   - Automatic browser opening
   - Network IP detection
   - Thread-safe server lifecycle

2. **Improved Spec File (`ExamSystem_Offline.spec`):**
   - Complete Flask dependency collection
   - Proper hidden imports
   - Optimized exclusions
   - Better packaging structure

3. **Automated Build Script (`build_offline.ps1`):**
   - One-command building
   - Prerequisite checking
   - Automatic PyInstaller installation
   - Distribution package creation
   - Build verification

### Distribution

**To distribute to users:**

1. Extract `ExamSystem-Offline-YYYY-MM-DD_HH-mm-ss.zip`
2. Copy the extracted `ExamSystem` folder to USB/network
3. Users just double-click `ExamSystem.exe`
4. Server starts automatically
5. Browser opens to the application

### Key Features

✅ **No Installation Required** - Just run the EXE  
✅ **Fully Offline** - No internet needed  
✅ **Graceful Shutdown** - Press Ctrl+C to stop  
✅ **Network Access** - Shows network URL for student access  
✅ **Console Output** - See server status and errors  
✅ **Auto Browser** - Opens automatically when ready  

### Troubleshooting

**If build fails:**
- Ensure Python 3.7+ is installed
- Run: `pip install pyinstaller`
- Use `-Clean` flag to remove old builds

**If executable crashes:**
- Check console output for errors
- Ensure all folders (templates, static, data) are included
- Verify no antivirus blocking

**If port 5000 is busy:**
- Close other applications using port 5000
- Or modify launcher_offline.py to use different port

### Technical Details

**Build Process:**
1. PyInstaller collects Python runtime + dependencies
2. Bundles Flask app with all templates/static files
3. Creates single-folder distribution
4. Packages everything into ZIP file

**Based on:**
- School Scheduler repository patterns
- Flask production best practices
- PyInstaller bundling techniques

**Differences from Development:**
- Uses werkzeug.serving (production server)
- Graceful signal handling
- Thread-based server management
- No debug mode

### Need Help?

Check the console output when running the executable.  
All errors and status messages are shown there.

---

**Built:** 2026-02-05  
**Method:** PowerShell automation based on School Scheduler patterns
