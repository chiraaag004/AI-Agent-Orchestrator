@echo off
cls
REM This script starts all the necessary services for testing of the bot in a single window.

echo Starting testing services...

REM 1. Start the Streamlit Dashboard for monitoring.
echo Starting Dashboard...
start "" /b cmd /c "streamlit run apps/dashboard.py"

REM 2. Start the Streamlit Test App.
echo Starting Test App...
start "" /b cmd /c "streamlit run apps/streamlit_app.py"

REM Keep window alive (optional)
REM You can add logging or health check here later if needed.
REM pause