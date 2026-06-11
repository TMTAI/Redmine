@echo off

python check_env.py

if errorlevel 1 (
    echo Missing dependencies.
    echo Installing...

    python -m pip install -r requirements.txt
)

echo.
echo Running application...
echo.

python main.py

pause