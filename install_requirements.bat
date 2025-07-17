@echo off
echo ========================================
echo   Installing Python Dependencies
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing backend requirements...
pip install -r backend\requirements.txt

echo.
echo Installation complete!
echo.
echo You can now run: start_backend.bat
pause