# Simple Build Script for Exam System - Standalone Offline Version
# PowerShell

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " Exam System - Offline Build Script" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    exit 1
}

# Check PyInstaller
Write-Host "Checking PyInstaller..." -ForegroundColor Yellow
$pyinstallerCheck = python -c "import PyInstaller; print(PyInstaller.__version__)" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    python -m pip install pyinstaller
} else {
    Write-Host "PyInstaller found: $pyinstallerCheck" -ForegroundColor Green
}

# Clean previous build
Write-Host ""
Write-Host "Cleaning previous build..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
Write-Host "Clean complete" -ForegroundColor Green

# Build
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan  
Write-Host " Building executable (this may take 3-5 minutes)..." -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

python -m PyInstaller ExamSystem_Offline.spec --clean --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}

# Verify
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " Verifying build..." -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$exePath = "dist\ExamSystem\ExamSystem.exe"
if (Test-Path $exePath) {
    $size = [math]::Round((Get-Item $exePath).Length / 1MB, 2)
    Write-Host "SUCCESS: Executable created" -ForegroundColor Green
    Write-Host "Location: $exePath" -ForegroundColor White
    Write-Host "Size: $size MB" -ForegroundColor White
} else {
    Write-Host "ERROR: Executable not found!" -ForegroundColor Red
    exit 1
}

# Create README
$readmePath = "dist\ExamSystem\README.txt"
$readmeContent = @"
==================================================================
           Exam System - Standalone Offline Version               
==================================================================

QUICK START:
1. Double-click ExamSystem.exe
2. Browser will open automatically
3. Press Ctrl+C in console to stop server

NETWORK ACCESS:
The console will show a Network URL like: http://192.168.1.100:5000
Students can use this URL to access from other computers.

FOLDERS:
- templates/  : Web templates
- static/     : CSS, JS, images  
- data/       : Database
- Exams/      : Exam files
- video/      : Tutorial videos

NO INTERNET REQUIRED - Works fully offline!

Built: $(Get-Date -Format "yyyy-MM-dd HH:mm")
"@
$readmeContent | Out-File -FilePath $readmePath -Encoding UTF8 -Force

# Create ZIP
Write-Host ""
Write-Host "Creating distribution package..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$zipName = "ExamSystem-Offline-$timestamp.zip"

Compress-Archive -Path "dist\ExamSystem" -DestinationPath $zipName -Force

if (Test-Path $zipName) {
    $zipSize = [math]::Round((Get-Item $zipName).Length / 1MB, 2)
    Write-Host "SUCCESS: Distribution package created" -ForegroundColor Green
    Write-Host "Package: $zipName" -ForegroundColor White
    Write-Host "Size: $zipSize MB" -ForegroundColor White
} else {
    Write-Host "WARNING: Failed to create ZIP package" -ForegroundColor Yellow
}

# Done
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " BUILD COMPLETE!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Executable: dist\ExamSystem\ExamSystem.exe" -ForegroundColor White
Write-Host "Distribution: $zipName" -ForegroundColor White
Write-Host ""
Write-Host "To test: cd dist\ExamSystem && .\ExamSystem.exe" -ForegroundColor Yellow
Write-Host ""

# Ask to test
$test = Read-Host "Test executable now? (y/n)"
if ($test -eq "y") {
    Write-Host "Starting executable..." -ForegroundColor Yellow
    Set-Location "dist\ExamSystem"
    Start-Process "ExamSystem.exe"
}
