# MedConnect Development Server Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " MedConnect Development Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to find Python
function Find-Python {
    $pythonCommands = @('python', 'python3', 'py')
    
    foreach ($cmd in $pythonCommands) {
        try {
            $result = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $result -notmatch "Microsoft Store") {
                Write-Host "[OK] Python found: $cmd" -ForegroundColor Green
                Write-Host $result -ForegroundColor Gray
                return $cmd
            }
        } catch {
            continue
        }
    }
    
    # Try to find Python in common locations
    $pythonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
        "C:\Program Files\Python*\python.exe",
        "C:\Python*\python.exe",
        "$env:USERPROFILE\AppData\Local\Programs\Python\Python*\python.exe"
    )
    
    foreach ($path in $pythonPaths) {
        $found = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            Write-Host "[OK] Python found at: $($found.FullName)" -ForegroundColor Green
            return $found.FullName
        }
    }
    
    return $null
}

# Find Python
$pythonCmd = Find-Python

if (-not $pythonCmd) {
    Write-Host "[ERROR] Python is not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please do ONE of the following:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Install Python from https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "   Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Disable Windows Store alias:" -ForegroundColor White
    Write-Host "   - Open Settings > Apps > Advanced app settings" -ForegroundColor Gray
    Write-Host "   - Click 'App execution aliases'" -ForegroundColor Gray
    Write-Host "   - Turn OFF 'python.exe' and 'python3.exe'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Or activate your virtual environment first:" -ForegroundColor White
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "See FIX_PYTHON.md for detailed instructions." -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "manage.py")) {
    Write-Host "[ERROR] manage.py not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[INFO] Virtual environment found. Activating..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

Write-Host ""
Write-Host "[INFO] Running database migrations..." -ForegroundColor Yellow
& $pythonCmd manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Migration failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Starting Django Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& $pythonCmd manage.py runserver

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Server failed to start!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
