@echo off
echo Setting up The Elidoras Codex / Machine Goddess environment...

REM Activate virtual environment or use system Python
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt

REM Test WordPress connection
echo Testing WordPress connection...
python scripts\test_wordpress_connection.py

echo.
echo Setup complete. You can now run "python app.py" to start the application.
pause