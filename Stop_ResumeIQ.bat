@echo off
echo Stopping ResumeIQ background servers...

:: Safely kill only the specific Python process running our backend
powershell -Command "Get-CimInstance Win32_Process -Filter \"name='python.exe'\" | Where-Object { $_.CommandLine -match 'run.py' } | Invoke-CimMethod -MethodName Terminate" >nul 2>&1

:: Safely kill the Node/Vite processes for our frontend
powershell -Command "Get-CimInstance Win32_Process -Filter \"name='node.exe'\" | Where-Object { $_.CommandLine -match 'vite' -or $_.CommandLine -match 'npm' } | Invoke-CimMethod -MethodName Terminate" >nul 2>&1

echo.
echo Servers have been successfully stopped!
timeout /t 3 >nul
