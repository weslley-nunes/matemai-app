@echo off
echo Setting up the environment...

REM Define Python Path
set PYTHON_PATH=C:\Users\BOSS\.pyenv\pyenv-win\versions\3.12.9\python.exe

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo Python 3.12.9 not found at expected path: %PYTHON_PATH%
    echo Please check your python installation.
    pause
    exit /b
)

REM Create Virtual Environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    "%PYTHON_PATH%" -m venv venv
)

REM Upgrade pip inside venv
echo Upgrading pip...
.\venv\Scripts\python.exe -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
.\venv\Scripts\pip install streamlit pandas numpy

REM Run the App
echo Starting Matemai...
.\venv\Scripts\streamlit run app.py

pause
