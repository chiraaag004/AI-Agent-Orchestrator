@echo off
REM This script starts all the necessary services for the Hospitality Bot project.
REM It will open three separate command prompt windows for each service.

echo Starting all services...

REM 1. Start the Streamlit Dashboard for monitoring.
echo Starting Dashboard (streamlit run dashboard.py)...
start "Dashboard" cmd /k "streamlit run dashboard.py"

REM 2. Start ngrok to expose the local server to the internet for Twilio.
echo Starting ngrok (ngrok http 5000)...
start "ngrok" cmd /k "ngrok http 5000"

REM 3. Start the Twilio Flask App.
echo Starting Twilio App (python apps/twilio_app.py)...
start "Twilio App" cmd /k "python apps/twilio_app.py"

echo All services are launching in separate windows.