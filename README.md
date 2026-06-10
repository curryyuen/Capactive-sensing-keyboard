<img width="724" height="495" alt="image" src="https://github.com/user-attachments/assets/1b7ab07d-8593-4869-974d-f27fc0324b14" />
Here's a **detailed summary** of your BadUSB device project, covering the purpose, hardware, functionality, interface design, and user interaction.

---

## Project Overview

You are building a **portable BadUSB device** based on an **ESP32‑C3** microcontroller. It emulates a USB keyboard to inject pre‑written keystroke scripts (payloads) into a target computer. The device features a small **0.96‑inch IPS TFT display (80×160 pixels)** used in **horizontal/landscape orientation** (160×80 effective resolution), plus three physical buttons (Up, Down, Center) for navigation and execution.

All payload scripts are stored in the ESP32’s **LittleFS** file system as plain text files (`.txt`) using a simple Ducky‑Script‑like syntax. You can add, remove, or edit scripts without recompiling the firmware – simply upload new files to LittleFS via the Arduino IDE’s “ESP32 Sketch Data Upload” tool.

The device is battery‑powered (or USB‑powered) and enters **deep sleep** after 2 minutes of button inactivity to conserve power, waking up instantly when any button is pressed. The last viewed script index is saved in RTC memory so the device resumes where it left off.

---

## Hardware Components

| Component | Specification |
|-----------|---------------|
| **Microcontroller** | ESP32‑C3 (with native USB for HID keyboard emulation via TinyUSB) |
| **Display** | 0.96" IPS TFT, 80×160 pixels, SPI interface (driver e.g., ST7735, GC9A01) |
| **Buttons** | 3 tactile switches: Up, Down, Center (GPIOs 0, 1, 2 – all RTC‑capable for wake‑up) |
| **USB** | Connected to target computer (acts as a keyboard) |
| **Power** | Either from USB or battery (deep sleep ~10 µA) |

---

## Core Functionalities

### 1. Script Management (LittleFS)
- On boot, the ESP32 mounts LittleFS and scans the root directory for all files ending with `.txt`.
- It stores the filenames (without extension) in an internal array.
- The order is alphabetical by filename – you can name files like `01_ReverseShell.txt`, `02_WifiGrab.txt` to control the sequence.

### 2. User Interface (TFT – One Line)
The display shows a **single line** of information in landscape mode (160×80 pixels). The line is divided into three areas:

```
┌─────────────────────────────────────────────────┐
│  RevShell                         [2/5]  Ready  │
└─────────────────────────────────────────────────┘
```

- **Left section** – Script filename (e.g., `RevShell`). If the name exceeds about 12 characters, it is truncated with `…`.
- **Middle‑right section** – Counter showing `[current/total]` (e.g., `[2/5]`).
- **Rightmost section** – Status indicator, using short words:
  - `Ready` – idle, waiting for button input.
  - `Run?` – after first press of Center button (awaiting confirmation).
  - `Run…` – during script execution (may include a spinning character).
  - `Done` – after successful execution (displays for 1 second then returns to `Ready`).
  - `Err` – an error occurred (file missing, parse error, etc.).
  - `None` – no `.txt` scripts found in LittleFS.

### 3. Button Navigation & Script Selection
- **Up button** – moves to the previous script in the list. The display immediately updates the filename and counter. No animation except a quick visual flash (optional).
- **Down button** – moves to the next script.
- Buttons are debounced in software (50 ms). Presses reset the inactivity timer and cancel any pending execution confirmation.

### 4. Script Execution – Double‑Press Confirmation
To avoid accidental running of scripts, the device uses a **two‑press confirmation**:

1. **First short press** of the Center button → status changes to `Run?`. A 2‑second timeout starts.
2. **Second short press** of the Center button within 2 seconds → execution begins.
   - Status changes to `Run…`, buttons are disabled.
   - The selected script file is read from LittleFS and parsed line by line.
   - Keystrokes are sent to the computer via USB HID (keyboard emulation).
   - A simple spinner (e.g., rotating `| / - \`) can be shown in the status area to indicate activity.
3. **If the timeout expires** or **Up/Down is pressed** during the wait – the confirmation is cancelled, status returns to `Ready`.

### 5. Ducky Script Parser (Basic Commands)
The parser reads the script file line by line and supports these commands (case‑insensitive):

| Command | Syntax | Action |
|---------|--------|--------|
| `DELAY` | `DELAY 500` | Waits for the specified milliseconds (non‑blocking, allows spinner update). |
| `STRING` | `STRING Hello` | Types the given text (supports spaces, special characters). |
| `ENTER` | `ENTER` | Presses and releases the Return key. |
| `GUI` | `GUI` | Presses and releases the Windows/Command key (alone). For combinations like `GUI r`, you can split into two commands: `GUI`, `DELAY 50`, `r`. |
| `ALT` | `ALT` | Presses and releases the Alt key. For `ALT F4`: `ALT`, `DELAY 50`, `F4`. |
| `CTRL` | `CTRL` | Presses and releases the Ctrl key. |
| `SHIFT` | `SHIFT` | Presses and releases the Shift key. |
| `MENU` | `MENU` | Presses the context menu key (right‑click). |
| `REPEAT` | `REPEAT 3` | Repeats the previous command 3 times (useful for arrow keys). |

**Example script file (`01_RevShell.txt`):**
```
DELAY 2000
GUI r
DELAY 500
STRING powershell -NoP -NonI -W Hidden -Exec Bypass -Enc encodedcommand
ENTER
```

The parser ignores empty lines and lines starting with `//` (comments).

### 6. Deep Sleep & Wake‑up
- An inactivity timer (`lastActivity`) is updated on every button press.
- In the main loop, if the elapsed time exceeds **2 minutes** and no script is currently executing, the device enters deep sleep.
- Before sleeping:
  - The TFT is turned off (backlight off, display sleep mode).
  - The current script index (`currentIndex`) is saved to **RTC_DATA_ATTR** (persistent across deep sleep but not power cycle).
  - Wake‑up is configured on any of the three buttons (GPIOs 0,1,2) using `esp_sleep_enable_ext1_wakeup()` with `ESP_EXT1_WAKEUP_ANY_LOW` (since buttons are active low with pull‑ups).
- On wake, the ESP32 reboots and runs `setup()` again. It detects the wake‑up cause and restores `currentIndex` from RTC memory, then proceeds to scan LittleFS and show the correct script.

### 7. Error Handling
- **No LittleFS partition** → display `No FS` and halt.
- **No `.txt` files found** → display `No scripts` in the main area (status becomes `None`). Buttons do nothing except allow deep sleep.
- **Script file missing** (e.g., deleted after list was built) → on selection attempt, show `Err` and fall back to first available script.
- **Parser error** (unknown command) → show `Err` and abort execution, returning to `Ready`.

---

## User Interaction Walkthrough

1. **Plug the device** into a target computer’s USB port. The computer recognises it as a USB keyboard.
2. **Power on** (or wake from sleep). The TFT shows the first script filename, e.g., `RevShell`, counter `[1/5]`, status `Ready`.
3. **Navigate** using Up/Down to choose a different script. The display updates immediately.
4. **Execute**:
   - Press Center once → status changes to `Run?`.
   - Within 2 seconds, press Center again → status `Run…`, script executes.
   - While running, the spinner rotates and all other buttons are ignored.
   - After finishing, status shows `Done` for 1 second, then returns to `Ready`.
5. **Cancel execution**: After first Center press, press Up/Down or wait 2 seconds → status returns to `Ready`.
6. **Idle**: If no button is pressed for 2 minutes, the device enters deep sleep. Press any button to wake and resume.

---

## Code Structure (Planned)

The final Arduino sketch (`.ino`) will contain:

- **Libraries**: `TFT_eSPI`, `FS`, `LittleFS`, `USBHIDKeyboard` (TinyUSB), `esp_sleep`.
- **Global variables**: script list array, current index, last activity timestamp, execution flag, confirmation state, etc.
- **Setup()**:
  - Initialise serial, TFT, buttons.
  - Mount LittleFS, scan for `.txt` files.
  - Restore saved index from RTC.
  - Show first script.
- **Loop()**:
  - Read buttons with debouncing.
  - Handle Up/Down (change script, cancel confirm).
  - Handle Center (state machine: first press → confirm mode; second press → execute).
  - Update display (filename, counter, status, spinner).
  - Check inactivity → go to deep sleep.
- **Helper functions**:
  - `refreshDisplay()` – updates TFT with current data.
  - `executeScript(index)` – loads file, parses, types via USB.
  - `parseAndTypeLine(String line)` – interprets commands.
  - `updateSpinner()` – rotates the spinner character in status area.
  - `goToSleep()` – prepares and enters deep sleep.

---

## What You Get (When I Write the Code)

I will provide a **complete, well‑commented Arduino sketch** that:
- Works on **ESP32‑C3** with **TinyUSB HID**.
- Uses **TFT_eSPI** configured for your **80×160 IPS display** (you need to set the correct driver and pins in `User_Setup.h` – I’ll give guidance).
- Implements the **one‑line interface** exactly as described.
- Includes the **Ducky Script parser** with basic commands.
- Handles **deep sleep** and RTC memory for index persistence.
- Has **debounced buttons** and **double‑press confirmation**.

---

## Next Steps

If you **approve this design** and want the code, simply reply:  
**“Yes, write the code.”**

I’ll produce the full Arduino sketch, plus instructions for:
- Setting up the TFT_eSPI configuration for your display.
- Installing the LittleFS upload tool.
- Creating and uploading script `.txt` files.

If you want any changes (e.g., different status words, different timeout values, adding a beep), tell me now.
