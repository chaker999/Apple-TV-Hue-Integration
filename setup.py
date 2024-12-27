import os
import json
import subprocess
import sys
import webbrowser
import platform

CONFIG_FILE = "config.json"
REQUIREMENTS_FILE = "requirements.txt"
RUN_BAT_FILE = "run.bat"  # For Windows convenience

def main():
    # 1. Prompt for host/port if config.json missing
    if os.path.exists(CONFIG_FILE):
        print("Configuration already exists. Using existing config.json...")
        with open(CONFIG_FILE, "r") as cf:
            config = json.load(cf)
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 8888)
    else:
        # Prompt user for IP and Port
        host = input("Enter host IP address (default 127.0.0.1): ") or "127.0.0.1"
        port_input = input("Enter port (default 8888): ") or "8888"
        try:
            port = int(port_input)
        except ValueError:
            print("Invalid port. Using default 8888.")
            port = 8888

        config = {"host": host, "port": port}
        with open(CONFIG_FILE, "w") as cf:
            json.dump(config, cf, indent=2)
        print(f"Created {CONFIG_FILE} with IP={host} and Port={port}.")

    # 2. Install dependencies
    print("Installing dependencies from requirements.txt (if present)...")
    if os.path.exists(REQUIREMENTS_FILE):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])
    else:
        print(f"{REQUIREMENTS_FILE} not found! Skipping dependency install.")

    # 3. Create a run.bat for Windows convenience (optional)
    #    - This allows Windows users to double-click run.bat next time.
    #    - For Linux/macOS, they can still do `python app.py &` or create their own scripts.
    with open(RUN_BAT_FILE, "w") as bat:
        bat.write("@echo off\n")
        bat.write("echo Starting RnR Automation...\n")
        # Using pythonw to avoid console if user double-clicks run.bat:
        bat.write("start pythonw app.py\n")
        # Optionally open browser after 2s delay
        bat.write("timeout /t 2 >nul\n")
        bat.write(f"start http://{host}:{port}\n")

    print(f"Created {RUN_BAT_FILE} for Windows users to double-click in future.")

    # 4. Launch the app in a background/detached manner
    print("Launching app.py in background...")

    cmd = [sys.executable, "app.py"]  # e.g. ["python", "app.py"]
    system_name = platform.system().lower()

    if "windows" in system_name:
        # Use DETACHED_PROCESS so closing this console won't kill the child
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(
            cmd,
            creationflags=DETACHED_PROCESS,
            close_fds=True
        )
    else:
        # On macOS/Linux, just redirect stdout/stderr to /dev/null (or a log file)
        # so the parent can exit without waiting for the child.
        devnull = open(os.devnull, 'wb')
        subprocess.Popen(
            cmd,
            stdout=devnull,
            stderr=devnull,
            close_fds=True
        )

    # 5. Open browser
    url = f"http://{host}:{port}"
    print(f"Opening {url} in your browser...")
    webbrowser.open(url)

    # 6. Exit the setup script immediately so the child keeps running
    print("Setup complete! The app is running in the background.")
    print("Feel free to close this window if it doesn't close itself.")
    os._exit(0)

if __name__ == "__main__":
    main()
