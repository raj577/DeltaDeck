@echo off
echo ========================================
echo   Option Spreads Analyzer Backend
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Virtual environment activated!
echo Python location: 
where python

echo.
echo Starting FastAPI backend server...
cd backend
python main.py

echo.
echo Backend server stopped.
pause