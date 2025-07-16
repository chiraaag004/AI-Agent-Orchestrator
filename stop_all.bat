@echo off
REM This script stops all services started by run_all.bat.

echo Stopping all services...

echo Stopping ngrok...
REM Kill ngrok by its process name.
taskkill /F /IM ngrok.exe /T >nul 2>&1

echo Stopping Dashboard...
REM Kill the Dashboard window by the title we gave it in run_all.bat.
taskkill /F /FI "WINDOWTITLE eq Dashboard" /T >nul 2>&1

echo Stopping Twilio App...
REM Kill the Twilio App window by its title.
taskkill /F /FI "WINDOWTITLE eq Twilio App" /T >nul 2>&1

echo All running services have been requested to stop.