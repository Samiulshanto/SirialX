@echo off
set VENV_DIR=.venv
set MAIN_SCRIPT=SirialX.py
set REQUIREMENTS=requirements.txt

:: Switch to the directory where this script is located
cd /d "%~dp0"

:: Check if virtual environment exists
if not exist %VENV_DIR%\ (
    echo [*] Virtual environment not found. Creating one...
    python -m venv %VENV_DIR%
    
    echo [*] Installing requirements...
    call %VENV_DIR%\Scripts\activate
    pip install --upgrade pip
    if exist %REQUIREMENTS% (
        pip install -r %REQUIREMENTS%
    ) else (
        echo [!] requirements.txt not found. Skipping...
    )
    deactivate
)

:: Activate and run
call %VENV_DIR%\Scripts\activate
echo [*] Running %MAIN_SCRIPT%...
python %MAIN_SCRIPT%
deactivate
