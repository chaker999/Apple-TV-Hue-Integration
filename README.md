Apple TV and Hue Light Integration

This repository contains a Flask application that controls Apple TVs and Philips Hue lights, and also provides a system tray icon for easy management.

Table of Contents
Features
Requirements
Installation
Running the App
Windows
macOS & Linux
Configuration
FAQ & Troubleshooting
Contributing
License
Features
Apple TV Integration: Pair and monitor any Apple TV to automate Hue lights based on play/pause/stop states.
Hue Integration: Connect to a Hue Bridge, pair lights, and define rooms/scenes.
System Tray: A tray icon (via pystray) runs in the background, letting you right-click to exit or launch the web UI.
Flask Web UI: Easily manage Apple TV pairing, Hue bridges, and automation rules from a browser.
Cross-Platform: Works on Windows, macOS, and Linux (with a GUI environment for the tray icon).
Requirements
Python 3.7+
Internet/LAN access to your Apple TVs and Hue Bridge.
GUI Environment if you want to see the system tray icon (Windows, macOS, or desktop Linux). On headless Linux servers, the tray icon cannot appear.
Technologies used:

Flask (web framework)
pyatv (Apple TV integration)
phue (Philips Hue library)
pystray + Pillow (system tray icon)
Installation
Clone or Download this repository from GitHub:

bash
Copy code
git clone https://github.com/YourUsername/rnr-automation.git
cd rnr-automation
(Optional) Create and activate a Python virtual environment:

bash
Copy code
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
Run the Setup:

bash
Copy code
python setup.py
On Windows, you can just double-click setup.py if you prefer.
The setup script:
Prompts you for a host IP and port (the IP your Flask server should bind to).
Installs all required dependencies (requirements.txt).
Creates a config.json with your chosen IP/port.
Launches the app in a detached state, opening your browser to http://<host>:<port>.
Closes the setup console automatically, leaving the Flask app + tray icon running in the background.
Next Steps:

If everything goes well, your browser should open automatically, showing the index or “Pair” page.
The system tray icon (a small icon) should appear in your desktop’s system tray/menubar area.
Running the App
Windows
After the first install, you’ll see a file called run.bat in your folder.
Simply double-click run.bat to launch the app in a new console. It will:
Start the Flask + tray icon.
(Optional) open a browser automatically.
If you want it to keep running after you close the console, edit run.bat to use pythonw app.py or use the built-in start commands in the script.
macOS & Linux
No .bat file is created for non-Windows. Instead, you can simply do:
bash
Copy code
python app.py &
or
bash
Copy code
nohup python app.py &
if you want to run it in the background.
You can also create your own small shell script if desired:
bash
Copy code
#!/usr/bin/env bash
echo "Starting RnR Automation..."
python app.py &
sleep 2
xdg-open "http://127.0.0.1:8888"  # or open on macOS
Save it as run.sh, then chmod +x run.sh.
Note: If you want the tray icon to be visible, you need a desktop environment (like Gnome, KDE, or macOS Finder). On headless Linux servers, there’s no system tray for icons.

Configuration
config.json:
After the setup, a file named config.json is created with:

json
Copy code
{
  "host": "127.0.0.1",
  "port": 8888
}
Adjust these as needed. If you delete config.json and rerun setup.py, you’ll be prompted again.

requirements.txt:
Lists all needed dependencies (Flask, pyatv, phue, pystray, Pillow, etc.).

FAQ & Troubleshooting
I see the tray icon on Windows, but when I close the console, the app stops.

By default, run.bat uses python. If you close that console, Windows kills the child. Use pythonw or a “detached” approach (e.g., start pythonw app.py) so the app continues in the background.
On Linux, I don’t see a system tray icon.

You need a desktop environment with a system tray/menubar. Headless servers can’t show a tray icon. Alternatively, use the web UI alone.
Where do logs go if I want to debug?

If you run python app.py in a console, you’ll see logs in the terminal. For background modes, consider redirecting output to a file (e.g., python app.py > app.log 2>&1 & on Linux).
How do I fully stop the app?

Use the system tray right-click -> “Exit” menu, or find the Python process and kill it.
Why can’t I connect from another device on my network?

Make sure your host is set to 0.0.0.0 or your LAN IP so that external devices can reach it. Also ensure your firewall allows inbound traffic on the selected port.
Contributing
Fork the repo
Create your feature branch: git checkout -b my-new-feature
Commit your changes: git commit -am 'Add some feature'
Push to the branch: git push origin my-new-feature
Create a new Pull Request
We appreciate any improvements or bug fixes!

License
This project is licensed under the MIT License. See the LICENSE file for details.

