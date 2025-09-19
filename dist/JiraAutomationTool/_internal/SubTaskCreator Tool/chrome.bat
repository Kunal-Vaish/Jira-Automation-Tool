@echo off
REM Paths — change these to your real paths
set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
set "EXT_PATH=%~dp0jira_us_creator_with_points"
set "TMP_PROFILE=%TEMP%\jira_ext_profile"
 
REM Remove previous temp profile for a fresh start (optional)
rmdir /s /q "%TMP_PROFILE%" 2>nul
 
mkdir "%TMP_PROFILE%" 2>nul
 
REM Launch Chrome with a dedicated user-data-dir so a new process starts and extension is loaded.
start "" "%CHROME_PATH%" --user-data-dir="%TMP_PROFILE%" --disable-extensions-except="%EXT_PATH%" --load-extension="%EXT_PATH%" "https://jira.bell.corp.bce.ca/secure/Dashboard.jspa"
exit /b