@echo off
echo Starting Backend Server...
start "Backend API" python server.py

echo Starting Frontend UI...
cd dashboard_react
start "Frontend UI" npm run dev

echo Done! Open http://localhost:5173 in your browser.
pause
