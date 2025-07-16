import subprocess
import signal
import time
import os

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_console()

# Start Streamlit Dashboard
print("Launching Streamlit Dashboard...")
dashboard = subprocess.Popen(["streamlit", "run", "apps/dashboard.py"])

# Start Streamlit App
print("Launching Streamlit App...")
app = subprocess.Popen(["streamlit", "run", "apps/streamlit_app.py"])

try:
    print("\n✅ All services running. Press Ctrl+C to shut down. ✅\n")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")

    print("Stopping Streamlit Dashboard...")
    dashboard.send_signal(signal.SIGTERM)

    print("Stopping Streamlit App...")
    app.send_signal(signal.SIGTERM)

    dashboard.wait()
    app.wait()
    print("\n✅ All services stopped. ✅\n")