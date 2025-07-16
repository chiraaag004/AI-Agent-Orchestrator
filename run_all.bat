@echo off
REM This script starts all the necessary services for the Hospitality Bot project.
REM It will open three separate command prompt windows for each service.

echo Starting all services...

REM 1. Start the Streamlit Dashboard for monitoring.
echo Starting Dashboard (streamlit run apps/dashboard.py)...
start /min "Dashboard" streamlit run apps/dashboard.py

REM 2. Start ngrok to expose the local server to the internet for Twilio.
echo Starting ngrok (ngrok http 5000)...
start /min "ngrok" ngrok http --url=vertically-humble-dogfish.ngrok-free.app 5000

REM 3. Start the Twilio Flask App.
echo Starting Twilio App (python apps/twilio_app.py)...
start /min "Twilio App" python apps/twilio_app.py

echo All services are launching in separate windows.