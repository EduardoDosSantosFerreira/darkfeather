# DarkFeather - Wireless Connection PRO

DarkFeather is a graphical tool developed in Python with Tkinter to view and extract detailed information from Wi-Fi networks saved on Windows systems.

## Features

- View all Wi-Fi networks saved on Windows.
- Extract password (ASCII and HEX), authentication, encryption, and connection type.
- Identify the network adapter name and its GUID.
- Display profile file path and last modification date.
- Modern dark mode graphical interface.
- Quick copy window with "Copy" button to facilitate information sharing.
- "Search and Refresh" button to scan and display networks.
- "Reset UI" button to clear the display.

## Requirements

- **Operating System**: Windows
- **Python**: 3.7 or higher
- **Python Libraries**:
  - `tkinter` (standard in Python)
  - `wmi`

To install `wmi`, run:

```bash
pip install wmi
```

## How to Use

1. **Clone the repository** or copy the files to your machine:

```bash
git clone https://github.com/your-username/darkfeather.git
cd darkfeather
```

2. **Run the main script** as administrator:

```bash
python darkfeather.py
```

> The script requires administrative privileges to access system network profiles (`netsh` and Windows XML files).

3. Click on **Search and Refresh** to list all saved networks.
4. **Double-click** any field to open a window with a copy button.

## Project Structure

```
darkfeather/
├── darkfeather.py         # Main script with interface and logic
├── README.md              # This file
```

## Security

This tool does not attack networks; it only displays data saved locally on your own system. Ideal for technicians, support professionals, or those curious about networks they have previously connected to.

## Motivation

Inspired by tools like WirelessKeyView, DarkFeather aims to provide a modern, open-source alternative with a pleasant interface and full control over the information.

## Author

**Eduardo dos Santos Ferreira**
Python Developer | Cybersecurity | Systems and Automation
[LinkedIn](https://linkedin.com/in/eduardo-dos-santos-ferreira) • GitHub: [@eduardodossantosferreira](https://github.com/eduardodossantosferreira)

## License

This project is licensed under the MIT License