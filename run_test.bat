@echo off
cls
REM This script starts all the necessary services for testing of the bot in a single window.

echo Starting testing services...

REM 1. Start the Streamlit Dashboard for monitoring.
echo Starting Dashboard (streamlit run apps/dashboard.py)...
start /min "Dashboard" streamlit run apps/dashboard.py

REM 2. Start the Streamlit Test App.
echo Starting Test App (streamlit run apps/streamlit_app.py)...
start /min "Test App" streamlit run apps/streamlit_app.py

echo All services are launching in separate windows.