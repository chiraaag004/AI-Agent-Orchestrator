import subprocess
import signal
import time

# Start Streamlit Dashboard
print("Launching Streamlit Dashboard...")
dashboard = subprocess.Popen(["streamlit", "run", "apps/dashboard.py"])

# Start ngrok tunnel
print("Launching ngrok tunnel...")
ngrok = subprocess.Popen(["ngrok", "http", "--url=vertically-humble-dogfish.ngrok-free.app", "5000"])

# Start Twilio Flask App
print("Launching Twilio Flask App...")
twilio_app = subprocess.Popen(["python", "apps/twilio_app.py"])

try:
    print("\n✅ All services running. Press Ctrl+C to shut down.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down services...")

    dashboard.send_signal(signal.SIGINT)
    ngrok.send_signal(signal.SIGINT)
    twilio_app.send_signal(signal.SIGINT)

    dashboard.wait()
    ngrok.wait()
    twilio_app.wait()

    print("All services stopped.")