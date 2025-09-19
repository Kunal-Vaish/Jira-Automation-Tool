@echo off
set VENV_DIR=%~dp0.venv
call "%VENV_DIR%\Scripts\activate.bat"
python "%~dp0upload_jira.py"
pause