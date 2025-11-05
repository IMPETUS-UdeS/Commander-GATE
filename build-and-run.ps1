# One-step builder/runner for CTCommander on Windows
# Behavior:
#  - If dist\CTCommander.exe exists -> run it
#  - Else: create venv, install deps, try to build EXE
#  - If EXE build fails -> fall back to running via Python (venv) so users can still use the app

$ErrorActionPreference = "Stop"

function Write-Header($text) {
  Write-Host ""
  Write-Host "=== $text ===" -ForegroundColor Cyan
}

# Resolve repo root (this script's folder)
Set-Location -Path $PSScriptRoot
$repoRoot = Get-Location

# Paths
$venvDir     = Join-Path $repoRoot ".venv"
$venvPy      = Join-Path $venvDir "Scripts\python.exe"
$exePath     = Join-Path $repoRoot "dist\CTCommander.exe"
$mainPy      = Join-Path $repoRoot "CTCommander.py"
$reqFile     = Join-Path $repoRoot "requirements.txt"

function Ensure-Python {
  Write-Header "Checking Python"
  $py = Get-Command python -ErrorAction SilentlyContinue
  if (-not $py) {
    Write-Host "Python not found. Please install Python 3.12 (64-bit) and check 'Add Python to PATH' during setup:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/windows/"
    throw "Python not found on PATH"
  }
}

function Ensure-Venv {
  Write-Header "Ensuring virtual environment (.venv)"
  if (-not (Test-Path $venvDir)) {
    python -m venv ".venv"
  }
  if (-not (Test-Path $venvPy)) {
    throw "Virtual environment seems corrupted (missing $venvPy). Delete .venv and try again."
  }
}

function Ensure-Dependencies {
  Write-Header "Installing/Updating dependencies in venv"
  & $venvPy -m pip install --upgrade pip
  if (Test-Path $reqFile) {
    & $venvPy -m pip install -r $reqFile
  } else {
    Write-Host "requirements.txt not found; installing minimal runtime..." -ForegroundColor Yellow
    & $venvPy -m pip install PyQt6
  }
}

function Try-Build-Exe {
  Write-Header "Building CTCommander.exe"
  # Ensure PyInstaller in venv
  & $venvPy -m pip install pyinstaller

  # Compose PyInstaller args
  $piArgs = @(
    "-n", "CTCommander",
    "--onefile",
    "--windowed",
    "--hidden-import", "PyQt6.sip",
    "main.py"
  )

  if (Test-Path (Join-Path $repoRoot "assets")) {
    $piArgs += @("--add-data", "assets;assets")
  }

  try {
    & $venvPy -m PyInstaller @piArgs
  } catch {
    Write-Host "PyInstaller build failed: $($_.Exception.Message)" -ForegroundColor Yellow
  }
}

function Run-Exe {
  Write-Header "Launching EXE"
  if (Test-Path $exePath) {
    & $exePath
    return $true
  }
  return $false
}

function Run-Python {
  Write-Header "Launching via Python (venv)"
  if (-not (Test-Path $mainPy)) {
    throw "Cannot find main.py at $mainPy"
  }
  & $venvPy "$mainPy"
}

# ---------- Main flow ----------
try {
  # If EXE already exists, just run it
  if (Test-Path $exePath) {
    if (Run-Exe) { exit 0 }
  }

  # Otherwise, set up env and try to build
  Ensure-Python
  Ensure-Venv
  Ensure-Dependencies
  Try-Build-Exe

  # If EXE now exists, run it; else fall back to Python
  if (-not (Run-Exe)) {
    Write-Host "No EXE found in dist\ (or build failed). Falling back to running via Python..." -ForegroundColor Yellow
    Run-Python
  }
} catch {
  Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
  Write-Host "Falling back to running via Python..." -ForegroundColor Yellow
  try {
    Ensure-Python
    Ensure-Venv
    Ensure-Dependencies
    Run-Python
  } catch {
    Write-Host "Fatal: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
  }
}