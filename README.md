# Apple-TV-Hue-Integration

Seamlessly integrate your **Apple TV** with **Philips Hue** lighting using a **Flask** web interface and a **system tray** icon.

![Python Versions](https://img.shields.io/badge/Python-3.7%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)

## Table of Contents
1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [License](#license)

---

## Features

- **Apple TV Control**: Automatically change Philips Hue lights based on Apple TV’s play, pause, or stop states.
- **Hue Integration**: Connect to a Hue Bridge, pair lights, and configure brightness settings per “room.”
- **Flask Web UI**: Easy browser interface for pairing Apple TVs and Hue lights.
- **System Tray Icon**: Runs quietly in the background, letting you right-click to “Launch Browser” or “Exit.”
- **Cross-Platform**: Works on Windows (tested) and should also run on macOS/Linux with a desktop environment.

---

## Requirements

1. **Python 3.7+**  
2. **Local Network Access** to your Apple TV and Hue Bridge.  
3. (Optional) A **GUI environment** for the tray icon (e.g., Windows Explorer, macOS Finder, or a Linux desktop).

---

## Installation

1. **Clone** or **download** this repository:
   ```bash
   git clone https://github.com/chaker999/Apple-TV-Hue-Integration.git
   cd Apple-TV-Hue-Integration
