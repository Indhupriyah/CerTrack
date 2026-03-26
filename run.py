"""CerTrack - Run development server."""
import os
import sys
import subprocess
import signal
from dotenv import load_dotenv

load_dotenv()

def kill_port_5002():
    """Kill any process using port 5002."""
    # Skip if this is the reloader subprocess
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        return
    try:
        result = subprocess.run(
            ["lsof", "-ti", ":5002"],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"Terminated process {pid} on port 5002")
                except:
                    pass
    except:
        pass

# Kill any existing process on port 5002 (only on initial run)
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    kill_port_5002()

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)

