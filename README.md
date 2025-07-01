
---

<div align="center">
  <h1>SirialX - The Ultimate TUI Serial Monitor for USB Microcontrollers</h1>
  <p>
    <strong>A fast, powerful, and modern terminal interface for debugging your ESP32, Arduino, Raspberry Pi Pico, and other USB serial devices.</strong>
  </p>
  <p>
    <a href="#-why-sirialx">Why SirialX?</a> •
    <a href="#-key-features">Features</a> •
    <a href="#-installation--running">Installation</a> •
    <a href="#-usage-workflow">Usage</a> •
    <a href="#-contributing">Contributing</a> •
    <a href="#-license">License</a>
  </p>
</div>

![SirialX Screenshot](https://github.com/Samiulshanto/SirialX/blob/main/Screenshot%202025-07-01%20122939.png)
*(**Note:** This is a placeholder image. Consider creating a GIF showing SirialX detecting a port, connecting, and restarting a device to showcase its features!)*

---

## 🤔 Why SirialX?

If you develop for microcontrollers like the **ESP32** or **Arduino**, you live in the serial monitor. But traditional tools can be clunky, slow, or buried inside a heavy IDE. **SirialX** is built to be the perfect companion for your hardware development workflow. It lives in your terminal, launches instantly, and provides the features you *actually* need, like one-click hardware resets and smart notifications, all through a polished and intuitive interface.

It's designed to replace your old serial monitor and become an indispensable tool for your projects.

## 📋 Table of Contents

*   [✨ Key Features](#-key-features)
*   [⚙️ Installation & Running](#-installation--running)
    *   [Prerequisites (Important!)](#prerequisites-important)
    *   [Method 1: The Easy Way (Windows)](#method-1-the-easy-way-windows)
    *   [Method 2: Manual Setup (All Platforms)](#method-2-manual-setup-all-platforms)
    *   [Method 3: Advanced (System-Wide Access on Windows)](#method-3-advanced-system-wide-access-on-windows)
*   [📖 Usage Workflow: From USB Plug-in to Debugging](#-usage-workflow-from-usb-plug-in-to-debugging)
    *   [Keyboard Shortcuts](#keyboard-shortcuts)
*   [🚀 Feature Deep Dive](#-feature-deep-dive)
    *   [The "No More Unplugging" USB Reset](#the-no-more-unplugging-usb-reset)
    *   [Instant IP Address Notifications over USB](#instant-ip-address-notifications-over-usb)
*   [📂 Project Structure](#-project-structure)
*   [🤝 Contributing](#-contributing)
*   [📜 License](#-license)

---

## ✨ Key Features

*   **🖥️ Modern TUI Interface:** A clean, mouse-aware, and organized layout built with Textual. It feels like a native app, but with the speed of a terminal.
*   **🔌 Smart USB Port Detection:** Automatically scans and lists available COM ports. It intelligently highlights common USB-to-Serial devices (CH340, CP210x, FTDI) and pre-selects the most likely candidate, getting you connected faster.
*   ⚡ **One-Click USB Device Reset:** The "Restart Device" button is a game-changer. It programmatically toggles the DTR/RTS lines to trigger a hardware reset on boards like the ESP32—**no more unplugging and replugging your USB cable!**
*   🚀 **High-Speed Data Logging:** Supports baud rates up to `921600` for capturing high-frequency sensor data or verbose debug logs from your device over USB.
*   🎨 **Advanced Log Viewer:**
    *   **High-Resolution Timestamps:** Every line from your device is timestamped (`HH:MM:SS.ms`) for precise analysis.
    *   **Full Color Support:** Displays ANSI color codes and rich text formatting sent from your microcontroller, making debug output readable and easy to parse.
*   🔔 **Smart Desktop Notifications (Windows):**
    *   Get native desktop pop-ups for critical events (Connect, Disconnect, Errors).
    *   **IP Address Sniffer:** Automatically detects when your Wi-Fi enabled device (like an ESP32) prints its IP address to the serial port and sends you a desktop notification. Grab your device's IP without even looking at the terminal!
*   🌙 **Dark/Light Mode:** Instantly toggle themes with the `d` key to match your OS or terminal settings.
*   📦 **Zero-Hassle Windows Setup:** Includes a `sirialx.bat` script that handles the entire setup process. Just double-click to run.

---

## ⚙️ Installation & Running

### Prerequisites (Important!)

1.  **Python 3.8+:** Make sure Python is installed on your system.
2.  **USB Drivers:** Your computer needs the correct drivers to communicate with your microcontroller. Many modern boards work out-of-the-box, but some common ones require a driver:
    *   **CH340/CH341:** Common on inexpensive Arduino Nano and ESP8266/ESP32 clones.
    *   **CP210x:** Used on many official ESP32 boards from Espressif and Silicon Labs.
    *   **FTDI:** Used on older or official Arduino boards.
    
    > **Note:** If your device doesn't show up in SirialX, the most likely cause is a missing USB driver.

### Method 1: The Easy Way (Windows)

This is the recommended method for most Windows users.

1.  **Download:** Clone this repository or download the source as a ZIP and extract it.
2.  **Run:** Navigate into the project folder and **double-click the `sirialx.bat` file.**

The first time you run it, the script will create a local Python environment and install all dependencies. Subsequent launches will be instant.

### Method 2: Manual Setup (All Platforms)

This method works for macOS, Linux, and advanced Windows users.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Samiulshanto/SirialX.git
    cd SirialX
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the venv
    python -m venv .venv

    # Activate it (use the command for your shell)
    # macOS/Linux:
    source .venv/bin/activate
    # Windows (CMD):
    .\.venv\Scripts\activate.bat
    # Windows (PowerShell):
    .\.venv\Scripts\Activate.ps1
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the app:**
    ```bash
    python SirialX.py
    ```

### Method 3: Advanced (System-Wide Access on Windows)

Set up SirialX to run from anywhere in your terminal.

1.  **Initial Setup:** Follow **[Method 2](#method-2-manual-setup-all-platforms)** to clone the project and install dependencies. Place the project folder in a permanent location (e.g., `C:\Tools\SirialX`).

2.  **Create Launcher:** Inside the `SirialX` folder, create a new file named `sirialx.cmd` and paste this into it:
    ```batch
    @echo off
    call "%~dp0.venv\Scripts\activate.bat"
    python "%~dp0SirialX.py" %*
    ```

3.  **Add to Windows PATH:**
    a. Press `Win + R`, type `sysdm.cpl`, and hit Enter.
    b. Go to the **Advanced** tab and click **Environment Variables...**.
    c. In the **System variables** list, select `Path` and click **Edit...**.
    d. Click **New** and add the full path to your `SirialX` project directory (e.g., `C:\Tools\SirialX`).
    e. Click OK on all windows to save.

4.  **Run:** Close and re-open any terminal windows. You can now launch the app from any directory by simply typing `sirialx`!

---

## 📖 Usage Workflow: From USB Plug-in to Debugging

Here is the typical step-by-step workflow for using SirialX:

1.  **Connect Your Device:** Plug your Arduino, ESP32, or other microcontroller into your computer's USB port.
2.  **Launch SirialX:** Run the application using one of the methods described above.
3.  **Select the USB Port:** Click the "Select Port" dropdown. SirialX will list all detected serial ports. Your device will often be identified by its USB-to-Serial chip, like `USB-SERIAL CH340 (COM5)` or `Silicon Labs CP210x... (COM3)`. SirialX will try to pre-select the most likely one.
4.  **Set the Baud Rate:** Select the baud rate that matches your `Serial.begin()` configuration (e.g., `115200`).
5.  **Connect:** Click the green "Connect" button. It will turn red, and you will see a confirmation message in the log.
6.  **View Serial Output:** As your device sends data with `Serial.println()`, it will appear in the "Serial Output" pane, complete with timestamps and colors.
7.  **Restart if Needed:** If your code gets stuck or you want to see the boot-up messages again, just click the "Restart Device" button. The device will reboot as if you had pressed its physical reset button.
8.  **Disconnect:** When you're done, click the red "Disconnect" button.

### Keyboard Shortcuts

| Key | Action             |
|-----|--------------------|
| `d` | Toggle Dark Mode   |
| `q` | Quit Application   |

---

## 🚀 Feature Deep Dive

### The "No More Unplugging" USB Reset

The single most useful feature for ESP32/ESP8266 development is the hardware reset button. It uses the DTR (Data Terminal Ready) and RTS (Request to Send) pins of the USB-to-Serial chip to pull the EN (Enable) and GPIO0 pins low/high in a specific sequence, forcing the microcontroller to reboot. **SirialX automates this entire process with a single click**, saving you from the constant cycle of unplugging and replugging your USB cable to see startup logs or recover from a crash.

### Instant IP Address Notifications over USB

When your IoT device connects to Wi-Fi, its first task is usually to print its assigned IP address to the serial port. Instead of keeping your eyes glued to the log, SirialX's reader thread scans all incoming data from the USB port for an IPv4 address pattern. The moment it detects one, it triggers a native desktop notification. You can be working in your code editor, and the IP will pop up, ready for you to access your device's web server or API.

---

## 📂 Project Structure

```
.
├── SirialX.py          # The main Textual application script.
├── requirements.txt    # Python dependencies for the project.
├── sirialx.bat         # Easy-run batch script for Windows.
├── sirialx.cmd         # (Optional) Launcher for adding to the system PATH.
└── README.md           # You are here!
```

