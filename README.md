# Trayify

Trayify is a lightweight utility for Linux that allows you to minimize any open window to the system tray using `pystray`, `xdotool`, and `xprop`. It's especially useful for managing cluttered desktops or backgrounding applications that you just want out of the way.

## Features

- Tray any selected window to the system tray.
- Restore windows from tray icons.
- Kill windows directly from tray icons.
- Unhide all trayed windows with a single click.
- Clean and graceful shutdown behavior, restoring windows first.

## Requirements

- Linux OS
- Python 3.x
- GTK
- Dependencies: Pillow, pystray
- System tools: xdotool, xwininfo, zenity, xprop

## Install

```bash
sudo apt install python3-pip xdotool xwininfo zenity x11-utils
pip install -r ./requirements.txt
```

## Run

```bash
python3 ./trayify.py
```

## License

MIT
