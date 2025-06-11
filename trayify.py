"""
Trayify - A lightweight tray-based window minimizer for X11 environments
"""

import signal
import sys
import os
from PIL import Image
import pystray
from icon_manager import IconManager
from window_manager import WindowManager

DEFAULT_ICON = '/usr/share/icons/Adwaita/32x32/apps/utilities-terminal-symbolic.symbolic.png'
MAIN_ICON = './logo.png'

window_manager = None

def main() -> None:
    """
    Entry point for the Trayify application. Initializes the icon and window managers,
    sets up the system tray icon, and starts the tray icon event loop.
    """
    global window_manager

    os.environ['PYSTRAY_BACKEND'] = 'gtk'

    try:
        image = Image.open(resource_path(MAIN_ICON))
    except Exception as e:
        print(f"Failed to load image icon: {e}")
        sys.exit(1)

    icon_manager = IconManager(None)
    window_manager = WindowManager(icon_manager)
    icon_manager.window_manager = window_manager

    main_icon = pystray.Icon("main", icon=image, title="Trayify")
    icon_manager.set_main_icon(main_icon)
    icon_manager.update_main_menu()

    try:
        main_icon.run()
    except KeyboardInterrupt:
        exit_gracefully(0)
    except Exception as e:
        print(f"Failed to run main icon: {e}")
        icon_manager.shutdown()
        sys.exit(1)

def exit_gracefully(signum: int = 0, _frame: object = None) -> None:
    """
    Graceful shutdown handler for signals.

    Args:
        signum (int): Signal number.
        _frame (object): Current stack frame (unused).
    """
    print("Gracefully exiting...")

    if window_manager:
        print("Shutting down Window Manager")
        window_manager.shutdown()

    exit(signum)

def resource_path(relative_path: str) -> str:
    """
    Constructs an absolute path to a resource, compatible with PyInstaller bundles.

    Args:
        relative_path (str): Path relative to the current directory or PyInstaller bundle.

    Returns:
        str: Absolute path to the resource.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    main()
