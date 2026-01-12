
# Whatsapp-Filter v2 (Cross-Platform)

Filter phone numbers to see which ones are registered on WhatsApp, using WhatsApp Web automation.

- Cross‑platform: **Windows, macOS, Linux**
- Browsers: **Chrome, Firefox, Edge**
- Modes:
  - `single` – one browser window
  - `onedriver` – one browser window shared across threads
  - `threaded` – multiple browser instances with profile cloning
- Features:
  - Interactive **setup wizard** (`--setup`)
  - Interactive **config menu** (`--config-menu`)
  - Headless / non‑headless modes
  - Config via `config.yaml` (or JSON)
  - WebDriver auto‑download (with manual override)
  - Logging with timestamps + run summaries

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Architecture Overview](#architecture-overview)  
3. [Installation](#installation)  
   - [Windows](#installation-on-windows)
   - [macOS](#installation-on-macos)
   - [Linux (Ubuntu/Debian)](#installation-on-linux-ubuntudebian)
4. [First-Time Setup](#first-time-setup)
5. [Configuration](#configuration)
   - [Config File Example](#config-file-example)
   - [Config Fields](#config-fields)
6. [Usage](#usage)
   - [Core Commands](#core-commands)
   - [Modes Explained](#modes-explained)
   - [Headless Mode](#headless-mode)
   - [Overriding Input/Output](#overriding-inputoutput)
   - [Examples](#examples)
7. [Browser & WebDriver Notes](#browser--webdriver-notes)
   - [Chrome](#chrome)
   - [Firefox](#firefox)
   - [Edge](#edge)
8. [File & Folder Layout](#file--folder-layout)
9. [Logs & Outputs](#logs--outputs)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

`whatsapp-filter` automates WhatsApp Web via Selenium to test if a list of phone numbers is registered on WhatsApp. It:

- Opens WhatsApp Web
- Navigates to `https://web.whatsapp.com/send?phone=NUMBER`
- Detects if the “invalid phone number” popup appears
- Optionally checks for conversation headers and network retry banners
- Splits numbers into:
  - **Valid (WhatsApp-registered)**  
  - **Invalid (not registered / invalid format)**

Typical use case: you have a file with many phone numbers and want to know which ones are active on WhatsApp.

---

## Architecture Overview

Main components:

- `whatsapp_filter/cli.py`  
  CLI entrypoint, setup wizard, config menu, and main run logic.

- `whatsapp_filter/config.py`  
  Loads/merges configuration from `config.yaml` (or JSON) and CLI overrides.

- `whatsapp_filter/drivers.py`  
  Creates Selenium WebDrivers (Chrome, Firefox, Edge) with per-profile directories and optional headless mode.

- `whatsapp_filter/whatsapp.py`  
  WhatsApp Web automation:
  - Waiting for login (QR scan)
  - Opening chats for numbers
  - Detecting invalid/valid states (invalid modal, retry banner, conversation header).

- `whatsapp_filter/modes.py`  
  Implements modes:
  - `single`
  - `onedriver` (multi-thread, one driver)
  - `threaded` (multi-thread, multi-driver with profile cloning).

- `whatsapp_filter/io_utils.py`  
  File I/O for input numbers, outputs, logs.

- `whatsapp_filter/logger.py`  
  Simple timestamped logging helper (INFO/DEBUG/WARN/ERROR).

---

## Installation

The project is distributed as a Python package with a console script `whatsapp-filter`.

### Requirements

- **Python 3.8+**
- A supported browser:
  - Chrome, Firefox, or Edge
- Internet access (for WhatsApp Web and `webdriver-manager` auto-download), or manual driver setup.

---

## Auto Installer

### Windows
Useage: Double Click `setup_windows.bat`
or
In Powershell
```command
cd C:\whatsapp-filter
.\setup_windows.bat
```

### macOS / Linux
```command
cd /path/to/whatsapp-filter
chmod +x setup_unix.sh      # once
./setup_unix.sh
```

## Installation on Windows

1. **Open PowerShell** and go to the project folder:

   ```powershell
   cd C:\whatsapp-filter
   ```
2. Create & activate a virtual environment (recommended):
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
If you get an execution policy error:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  .\.venv\Scripts\Activate.ps1
  ```
Install the package:
  ```powershell
  pip install -e .
  ```
Verify the CLI is available:
  ```powershell
  whatsapp-filter --help
  ```
---
## Installation on macOS

1. Open Terminal and go to the project folder:
  ```terminal
  cd /path/to/whatsapp-filter
  ```
2. Create & activate a virtual environment:
  ```terminal
  python3 -m venv .venv
  source .venv/bin/activate
  ```
3. Install the package:
  ```terminal
  pip install -e .
  ```
4. Verify:
  ```terminal
  whatsapp-filter --help
  ```
---
## Installation on Linux (Ubuntu/Debian)

1. Install Python & base packages (if needed):
  ```terminal
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip
  ```
2. Go to the project folder:
  ```terminal
  cd /path/to/whatsapp-filter
  ```
3. Create & activate a virtual environment:
  ```terminal
  python3 -m venv .venv
  source .venv/bin/activate
  ```
4. Install the package:
  ```terminal
  pip install -e .
  ```
5. Verify:
  ```terminal
  whatsapp-filter --help
  ```
6. (Optional but often useful) Install common GUI libs for Chrome/Firefox:
  ```linux
  sudo apt install -y \
  libnss3 \
  libatk-bridge2.0-0 \
  libgtk-3-0 \
  libx11-xcb1 \
  libxcomposite1 \
  libxcursor1 \
  libxdamage1 \
  libxi6 \
  libxtst6 \
  libdrm2 \
  libgbm1 \
  libasound2
```
---

## First-Time Setup

After installation, run the **interactive setup wizard**. This is identical on Windows/macOS/Linux (only the shell syntax differs).

### Windows (PowerShell)
```powershell
cd C:\whatsapp-filter
.\.venv\Scripts\Activate.ps1
whatsapp-filter --setup --auto-run-after-setup
```
### macOS / Linux (bash)
```terminal
cd /path/to/whatsapp-filter
source .venv/bin/activate
whatsapp-filter --setup --auto-run-after-setup
```
**What the setup does**
- Opens an interactive configuration menu:
  - Input file path (list of phone numbers)
  - Valid/invalid output paths
  - Browser: chrome / firefox / edge
  - Headless mode: yes/no
  - Mode: single / onedriver / threaded
  - Threads, chunk size
  - Optional driver_path (for manual WebDriver)
  - Log file path
- Writes `config.yaml` in the current directory.
- Creates:
  - data/input_numbers.txt (with sample commented numbers)
  - data/valid_numbers.txt
  - data/invalid_numbers.txt
- Runs a **WebDriver smoke test** (headless).
- If test passes and --auto-run-after-setup was used, it **runs once immediately**.
  If setup fails (e.g. WebDriver issues), it will tell you what to fix.

---

## Configuration
### Config File Example
After running setup, you’ll have a config.yaml similar to:
```config
# Configuration for whatsapp-filter

input: "data/input_numbers.txt"
valid_output: "data/valid_numbers.txt"
invalid_output: "data/invalid_numbers.txt"

browser: "chrome"        # chrome | firefox | edge
headless: false
delay: 2.0               # seconds between checks

mode: "single"           # single | onedriver | threaded
threads: 4
chunk_size: 50

driver_path: null        # or "C:\\WebDrivers\\chromedriver.exe" etc.
log_file: "run_log.txt"
```
### Config Fields
- `input (str, required)`
  Path to the input file with phone numbers (one per line). Comments/blank lines are ignored.
- `valid_output (str)`
  Where to write numbers detected as WhatsApp-registered.
- `invalid_output (str)`
  Where to write numbers detected as invalid/not registered.
- `browser (str)`
  One of: chrome, firefox, edge.
- `headless (bool)`
  true or false. Headless browsers run without a visible window.
- `delay (float)`
  Delay (in seconds) between checking individual numbers.
- `mode (str)`
  - `single:` one browser instance, sequential processing.
  - `onedriver:` one browser instance, multi-threaded, shared with a lock.
  - `threaded:` multiple browser instances, each thread with its own cloned profile.
- `threads (int)`
  Number of threads for onedriver and threaded modes.
- `chunk_size (int)`
  For threaded mode: how many numbers each worker processes per browser instance.
- `driver_path (str or null)`
  Path to a manual WebDriver executable (chromedriver, geckodriver, msedgedriver), or   null to auto-download via webdriver-manager.

---

## Usage
Once installed and configured, the CLI command is:
```command
whatsapp-filter [OPTIONS]
```
### Core Commands
- Show help:
```command
whatsapp-filter --help
```
- First-time setup + auto-run:
```command
whatsapp-filter --setup --auto-run-after-setup
```
- Setup only (no auto-run):
```command
whatsapp-filter --setup
```
- Open config menu (edit config.yaml):
```command
whatsapp-filter --config-menu
```
- Run using current config.yaml:
```command
whatsapp-filter
```
- Show CLI examples and exit:

```command
whatsapp-filter --show-examples
```

### Direct Commands

For Windows
```commands
# Normal (use config.yaml)
whatsapp-filter

# Force headless (ignores headless=false in config)
whatsapp-filter --headless

# Force a mode
whatsapp-filter --mode single
whatsapp-filter --mode onedriver --threads 4
whatsapp-filter --mode threaded --threads 4 --chunk-size 50

# Override input/output for this run only
whatsapp-filter -i data\my_numbers.txt --valid-output data\my_valid.txt --invalid-output data\my_invalid.txt
```

For macOS/Linux
```commands
# Normal (use config.yaml)
whatsapp-filter

# Headless
whatsapp-filter --headless

# Force mode
whatsapp-filter --mode single
whatsapp-filter --mode onedriver --threads 4
whatsapp-filter --mode threaded --threads 4 --chunk-size 50

# Override input/output just for this run
whatsapp-filter -i data/my_numbers.txt --valid-output data/my_valid.txt --invalid-output data/my_invalid.txt
```

---
## Modes Explained
1. **single mode**
- One browser instance.
- Processes numbers sequentially.
- Good for:
  - First login and profile creation.
  - Lower resource usage.
Example:
```example
whatsapp-filter --mode single
```
2. **onedriver mode**
- One browser instance.
- Multiple threads use the same driver with a lock.
- Good balance between speed and resource use.
Example:
```example
whatsapp-filter --mode onedriver --threads 4
```
3. **threaded mode**
- Multiple browser instances (one per worker).
- Uses **profile cloning** from a base `single` profile:
  - Run single mode once to log in.
  - Then threaded clones that logged-in profile into worker profiles.
- Fastest, but uses more resources.
Example sequence:
```example
# 1) Create/log in base profile
whatsapp-filter --mode single

# 2) Run multi-driver threaded
whatsapp-filter --mode threaded --threads 4 --chunk-size 50
```
---

## Headless Mode
You can configure headless in `config.yaml` or from CLI.
- In config (config.yaml):
```config
headless: true
```
- From CLI (overrides config):
```config
whatsapp-filter --headless
```
Headless is supported for:
- Chrome
- Firefox
- Edge (Chromium-based)
Useful for:
- Servers
- CI environments
- Running without a GUI.
---

## Overriding Input/Output

You can override `input`, `valid_output`, and `invalid_output` without changing the config file:
```command
whatsapp-filter \
  -i data/my_numbers.txt \
  --valid-output data/valid_my.txt \
  --invalid-output data/invalid_my.txt
```
These CLI values override the ones in config.yaml for that run only.

---

## Examples

### Windows + Chrome (PowerShell)
```powershell
cd C:\whatsapp-filter
.\.venv\Scripts\Activate.ps1

# First-time setup and auto-run
whatsapp-filter --setup --auto-run-after-setup

# Normal run later
whatsapp-filter

# One-driver threaded mode
whatsapp-filter --mode onedriver --threads 4

# Multi-driver threaded mode (after a single-mode run)
whatsapp-filter --mode single
whatsapp-filter --mode threaded --threads 4 --chunk-size 50

# Headless run
whatsapp-filter --headless

# Override input/output
whatsapp-filter -i data/custom_input.txt --valid-output data/valid_custom.txt --invalid-output data/invalid_custom.txt
```

### macOS + Chrome (bash)
```terminal
cd ~/whatsapp-filter
source .venv/bin/activate

whatsapp-filter --setup --auto-run-after-setup
whatsapp-filter
whatsapp-filter --mode onedriver --threads 4
whatsapp-filter --mode threaded --threads 4 --chunk-size 50
whatsapp-filter --headless
whatsapp-filter -i data/phones.txt --valid-output data/ok.txt --invalid-output data/bad.txt
```

### Linux (Ubuntu) + Firefox (bash)
```terminal
cd /opt/whatsapp-filter
source .venv/bin/activate

whatsapp-filter --setup --auto-run-after-setup
whatsapp-filter --mode single
whatsapp-filter --mode threaded --threads 3 --chunk-size 100
```
---

## Browser & WebDriver Notes
The project uses `webdriver-manager` to auto-download drivers where possible.
**Chrome**
- Install Chrome:
  - Windows: https://www.google.com/chrome/
  - macOS: `.dmg` from same site
  - Ubuntu: use `.deb` or repository instructions
- `webdriver-manager` will fetch **ChromeDriver** automatically.
If auto-download fails (e.g. proxy):

1. Download ChromeDriver matching your Chrome version: https://chromedriver.chromium.org/downloads

2. Place it:
    - Windows: C:\WebDrivers\chromedriver.exe
    - macOS/Linux: /usr/local/bin/chromedriver
3. Set driver_path in config or via --config-menu.

**Firefox**
- Install Firefox from your OS’s official source.
- webdriver-manager will fetch GeckoDriver automatically.
Manual fallback:
- Download GeckoDriver: https://github.com/mozilla/geckodriver/releases
- Place on PATH and set driver_path if needed.

**Edge**
- Install Microsoft Edge:
  - Windows/macOS: https://www.microsoft.com/edge
  - Linux: follow MS repo instructions.
- `webdriver-manager` will fetch Edge driver (msedgedriver) automatically.
Manual fallback:
- Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
- Place on PATH, set driver_path if needed.

---

## File & Folder Layout
After setup and at least one run, you’ll typically see:
```layout
project_root/
├─ pyproject.toml
├─ README.md
├─ config.yaml
├─ run_log.txt
├─ data/
│  ├─ input_numbers.txt
│  ├─ valid_numbers.txt
│  └─ invalid_numbers.txt
├─ browser_profiles/
│  ├─ chrome_whatsapp_profile_single
│  ├─ chrome_whatsapp_profile_worker_1
│  ├─ ...
└─ whatsapp_filter/
   ├─ __init__.py
   ├─ __main__.py
   ├─ logger.py
   ├─ config.py
   ├─ io_utils.py
   ├─ drivers.py
   ├─ whatsapp.py
   ├─ modes.py
   └─ cli.py
```
- `config.yaml` – main configuration.
- `data/` – input/output files.
- `browser_profiles/` – browser user data directories (WhatsApp sessions).
- `run_log.txt` – accumulated run summaries.
---

## Logs & Outputs

**Console Logging**

Uses a simple logger with timestamps, e.g.:
```logging
[2026-01-12 03:00:00] [INFO] Using config: AppConfig(...)
[2026-01-12 03:00:05] [INFO] Loaded 120 numbers from data/input_numbers.txt
[2026-01-12 03:00:06] [INFO] Mode: single
...
```
**Run Log File**

Each run appends a line to `log_file` (default `run_log.txt`), similar to:
```logging
Run finished: 2026-01-12 03:15:42 | Duration: 125.4s | Mode: single | Input: /path/to/data/input_numbers.txt | Valid: 80 -> /path/to/data/valid_numbers.txt | Invalid: 40 -> /path/to/data/invalid_numbers.txt
```

**Output Files**

- `valid_numbers.txt`: one valid number per line.
- `invalid_numbers.txt`: one invalid/unregistered number per line.
---

## Troubleshooting

**WebDriver errors / cannot create driver**

- Ensure your browser is installed (Chrome/Firefox/Edge).
- Check that webdriver-manager can download drivers:
  - If blocked by network, manually download and set driver_path.
- On Linux, make sure required libraries are installed (see [Linux install section](#installation-on-linux-ubuntudebian)).

**WhatsApp Web login timeout**

- When first running:
  - The tool opens WhatsApp Web and waits up to 3 minutes.
  - Make sure you scan the QR code in time.
- If it times out, it saves a screenshot (`whatsapp_login_timeout.png`) for debugging.

**Too slow / want faster runs**

- Try onedriver or threaded modes:
  - onedriver:
  ```command
  whatsapp-filter --mode onedriver --threads 4
  ```
  - threaded (after a single run):
  ```command
  whatsapp-filter --mode single
  whatsapp-filter --mode threaded --threads 4 --chunk-size 50
  ```
- Decrease delay in config (e.g., from 2.0 to 0.5), but be mindful of rate limits and stability.

**Too many browser windows**

- Use `single` or `onedriver` mode instead of `threaded`.
- Or reduce threads in config or via CLI.

## Disclaimer

This project is provided “as is” for educational and informational purposes only. Use of this tool may be subject to WhatsApp’s Terms of Service and local laws. The author assumes no responsibility or liability for any misuse, account restrictions, data loss, or legal issues arising from the use of this software. Use at your own risk.
