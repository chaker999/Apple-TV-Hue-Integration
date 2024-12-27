# Apple-TV-Hue-Integration

Seamlessly integrate your **Apple TV** with **Philips Hue** lighting via a **Flask** web interface and a **system tray** icon for convenient, background operation.

![Python Versions](https://img.shields.io/badge/Python-3.7%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Usage](#usage)
   - [Windows](#windows)
   - [macOS--linux](#macos--linux)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)
8. [License](#license)

---

## Overview

This project connects **Apple TVs** and **Hue Bridges** under one roof:
- A simple **Flask** server hosts a web dashboard for pairing and configuration.
- A **system tray icon** (via [pystray](https://pypi.org/project/pystray/)) runs in the background, letting you right-click to “Launch Browser” or “Exit.”
- When your Apple TV changes state (Play, Pause, Stop), the Hue lights in that “room” automatically adjust brightness accordingly.

**Tested on Windows**, but should also work on macOS and Linux (with a desktop environment for the tray). For headless servers (e.g., Linux without a GUI), you can still use the Flask web UI, but the tray icon will not be visible.

---

## Features

- **Apple TV Control**: Pair with one or more Apple TVs to detect play/pause/stop states.
- **Hue Integration**: Connect to a Hue Bridge, select lights, and define room-specific brightness presets.
- **Automated Lighting**: Lights brighten, dim, or turn off based on Apple TV activity.
- **Flask Dashboard**: Manage everything in your browser—no manual edits required.
- **System Tray**: Runs quietly in the background, freeing up your terminal.

---

## Requirements

1. **Python 3.7+**  
2. **Local Network**: Apple TVs and Hue Bridge must be on the same LAN as your computer.
3. **Graphical Desktop** (for tray icon): On Windows/macOS or a Linux desktop environment.

---

## Installation

You can either **clone** this repository or **download the ZIP**:

```bash
git clone https://github.com/chaker999/Apple-TV-Hue-Integration.git
cd Apple-TV-Hue-Integration
If you download the ZIP, extract it to a folder of your choice.

Run Setup
Find where you extracted/cloned the repository.
Open a Command Prompt (Windows) or Terminal (macOS/Linux) in that folder.
On Windows:

bash
Copy code
cd Apple-TV-Hue-Integration
python setup.py
(Press Enter after each command.)

If Python isn’t recognized, ensure it’s installed (3.7 or higher) and in your PATH.
During setup:

You’ll be prompted for a host IP (default: 127.0.0.1) and a port (default: 8888).
The script installs dependencies from requirements.txt.
It launches the Flask server in a detached process—no console needed.
Opens your default browser to http://<host>:<port>.
Closes its own setup console automatically when finished.
Look for the system tray icon (Windows typically places new icons in the “hidden icons” area).
The web dashboard should be open in your browser. If not, manually visit http://<host>:<port>.

Future Launches
On Windows, the script creates a run.bat file for you to double-click next time.
On macOS/Linux, simply run:
bash
Copy code
python app.py &
(or python setup.py again, although setup is only needed once).
Usage
Windows
After the first install, find run.bat in the project folder.
Double-click run.bat:
Starts app.py in a console.
The system tray icon appears near the clock.
Possibly opens the browser automatically (depending on how run.bat is configured).
Closing the console will kill the app if using python.
If you want it to keep running after you close the console, edit run.bat to use pythonw app.py, or:

bat
Copy code
start pythonw app.py
start http://127.0.0.1:8888
exit
This approach lets you close the run.bat window without stopping the background process.

macOS & Linux
No .bat file is created here. Instead:

bash
Copy code
# Start the app in the background
python app.py &

# or
nohup python app.py &
If you have a desktop environment, the tray icon should appear in the menubar (macOS) or system tray (GNOME/KDE on Linux).
On a headless Linux server, the tray icon won’t show (no GUI). The Flask server still runs, though.
Access it in your browser from any machine that can reach the server’s IP.
Configuration
config.json
Automatically generated by setup.py:

json
Copy code
{
  "host": "127.0.0.1",
  "port": 8888
}
host: the IP address your Flask server binds to.
port: the TCP port to listen on (default 8888).
requirements.txt
Lists your Python dependencies:

Flask
pyatv
phue
pystray
Pillow
…and possibly more. These are installed automatically when you run setup.py.

Troubleshooting
Tray Icon Missing
Check “hidden icons” on Windows or look for the menubar icon on macOS.
Ensure you’re running on a graphical desktop environment.

Closing the Console Kills the App (Windows)
By default, if you run python app.py in a standard console, closing it ends the process.
Use pythonw.exe or DETACHED_PROCESS flags to keep it running after the console closes.
The run.bat approach can be modified to:

bat
Copy code
start pythonw app.py
…which spawns a new, detached process.

Cannot Reach the Web Dashboard
Make sure the host in config.json is accessible (e.g., 0.0.0.0 if you want to connect from other devices).
Disable or configure your firewall if needed.

No Logs
If you need real-time logs, run python app.py in a normal console to see output.
For a background process, consider redirecting output to a file (e.g., nohup python app.py > app.log 2>&1 & on Linux/macOS).

Headless Linux
No tray icon is possible without a GUI. You can still use the web UI for all interactions.

License
This project is licensed under the MIT License.
You’re free to copy, modify, and distribute as long as you retain the original license text.

Enjoy controlling your Apple TV and Hue lights from one unified interface!
Feel free to open an issue or create a pull request if you have improvements or run into any problems.




I will not be able to trouble shoot macOS or Linux OS.  