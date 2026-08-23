@echo off
echo Starting ResumeIQ Servers...

:: Start the Flask Backend in a new terminal window
start "ResumeIQ Backend" cmd /k "cd backend && .\venv\Scripts\activate && python run.py"

:: Start the React Frontend in a new terminal window
start "ResumeIQ Frontend" cmd /k "cd frontend && npm run dev"

echo Both servers are starting up! 
echo The frontend will open in your browser shortly (or go to http://localhost:5173).
echo You can close this small window, but keep the two new server windows open while you use the app.
timeout /t 5 >nul
