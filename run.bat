@echo off
setlocal enabledelayedexpansion

:: Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Check for required files
if not exist "%SCRIPT_DIR%\requirements.txt" (
    echo Error: requirements.txt file not found
    exit /b 1
)

if not exist "%SCRIPT_DIR%\run.py" (
    echo Error: run.py file not found
    exit /b 1
)

:: Set virtual environment directory
set "VENV_DIR=%SCRIPT_DIR%\venv"

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Error: Python is not installed or not in PATH
        exit /b 1
    )
)

:: Create virtual environment if needed
if not exist "%VENV_DIR%\" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo Virtual environment creation failed
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call "%VENV_DIR%\Scripts\activate.bat"
) else (
    echo Error: Virtual environment activation script not found
    exit /b 1
)

:: Verify activation
python -c "import os; print('OK' if 'VIRTUAL_ENV' in os.environ else 'FAIL')" | find "OK" >nul
if %errorlevel% neq 0 (
    echo Error: Virtual environment activation failed
    exit /b 1
)

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Error: pip upgrade failed
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
python -m pip install -r "%SCRIPT_DIR%\requirements.txt"
if %errorlevel% neq 0 (
    echo Error: Dependency installation failed
    exit /b 1
)

:: Execute Python script
echo Starting run.py...

if "%~1"=="" (
    echo No target directory provided, Python will prompt for input
    python "%SCRIPT_DIR%\run.py"
) else (
    echo Using target directory: "%~1"
    python "%SCRIPT_DIR%\run.py" "%~1"
)
set EXIT_STATUS=%errorlevel%

:: Deactivate virtual environment
echo Deactivating virtual environment...
deactivate

echo Script execution completed
exit /b %EXIT_STATUS%
