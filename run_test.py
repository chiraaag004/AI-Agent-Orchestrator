import subprocess
import signal
import time

# Start Streamlit Dashboard
print("Launching Streamlit Dashboard...")
dashboard = subprocess.Popen(["streamlit", "run", "apps/dashboard.py"])

# Start Streamlit App
print("Launching Streamlit App...")
app = subprocess.Popen(["streamlit", "run", "apps/streamlit_app.py"])

try:
    print("\n✅ All services running. Press Ctrl+C to shut down.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")

    dashboard.send_signal(signal.SIGTERM)
    app.send_signal(signal.SIGTERM)

    dashboard.wait()
    app.wait()
    print("All services stopped.")