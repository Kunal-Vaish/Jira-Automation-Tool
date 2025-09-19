@echo off
REM ---------------------------
REM Slim .venv Cleanup Script
REM ---------------------------

SET VENV_PATH=%~dp0.venv\Lib\site-packages

echo Starting cleanup of .venv...

REM 1️⃣ Remove all __pycache__ folders
for /d /r "%VENV_PATH%" %%i in (__pycache__) do rd /s /q "%%i"

REM 2️⃣ Remove all tests folders
for /d /r "%VENV_PATH%" %%i in (tests) do rd /s /q "%%i"
for /d /r "%VENV_PATH%" %%i in (test) do rd /s /q "%%i"

REM 3️⃣ Remove .dist-info and .egg-info folders
for /d /r "%VENV_PATH%" %%i in (*.dist-info) do rd /s /q "%%i"
for /d /r "%VENV_PATH%" %%i in (*.egg-info) do rd /s /q "%%i"

REM 4️⃣ Remove pip, setuptools, wheel (optional if no further installs needed)
rd /s /q "%VENV_PATH%\pip"
rd /s /q "%VENV_PATH%\setuptools"
rd /s /q "%VENV_PATH%\wheel"

REM 5️⃣ Remove unused big packages (optional)
REM rd /s /q "%VENV_PATH%\numpy"
REM rd /s /q "%VENV_PATH%\matplotlib"

echo Cleanup complete. Check .venv folder size.
pause