Apple-TV-Hue-Integration
Seamlessly integrate your Apple TV with Philips Hue lighting, using a Flask web interface and a system tray icon for quick, background operation.
Note: This app has primarily been tested on Windows. It may work on macOS and Linux, but is not officially tested on those systems.

Features

Apple TV Control: Automatically change Philips Hue lights based on Apple TV’s play/pause/stop states.
Hue Integration: Connect to your Hue Bridge, pair lights, and configure brightness settings for each “room.”
Flask Web UI: A browser-based interface for easy configuration.
System Tray Icon: The app runs in the background so you can right-click the tray icon to open the browser or exit.
Cross-Platform: Developed and tested on Windows. Mac & Linux users may still run it with some tweaks.

Requirements

Python 3.7 or higher

If you don’t have Python installed, download it here or install via your OS package manager.
Local Network Access

Your Apple TV and Hue Bridge should be on the same network as your PC.

Windows Installation

Follow these steps to install and run on Windows using a ZIP file:

Download the ZIP

Go to the GitHub Releases/Code page and download the zip file.
Extract the ZIP

Unzip it into any folder of your choice, e.g. C:\AppleTVHue\.
Open Command Prompt

Press Win + R, type cmd, and press Enter.
Navigate to the Folder

In Command Prompt, type:
bash
Copy code
cd C:\AppleTVHue
(Replace C:\AppleTVHue with the actual path you unzipped.)
Run the Setup

Install the required packages and configure the app by typing:
bash
Copy code
python setup.py
If python isn’t recognized, ensure Python 3.7+ is installed and available in your PATH.
During setup, you’ll be prompted to enter a host IP (default: 127.0.0.1) and a port (default: 8888).
The script installs dependencies, launches the Flask app in the background, and opens your browser.
Watch for the Tray Icon

Look in your Windows system tray (near the clock). You should see a small icon representing this app.
Right-click the icon to “Launch Browser” or “Exit.”
