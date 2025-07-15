@echo off
echo Starting Moodly Flask Application...
cd /d "d:\PLP Academy\Moodly_App"

echo Checking and installing dependencies...
"D:/PLP Academy/Moodly_App/.venv/Scripts/pip.exe" install --upgrade pip
"D:/PLP Academy/Moodly_App/.venv/Scripts/pip.exe" install -r requirements.txt

echo Starting the application...
"D:/PLP Academy/Moodly_App/.venv/Scripts/python.exe" moodly_app.py
pause
