import os
import pystray
import subprocess
import threading
import time
import uuid
from PIL import Image
from typing import Optional

DEFAULT_ICON = '/usr/share/icons/Adwaita/32x32/apps/utilities-terminal-symbolic.symbolic.png'

class IconManager:
    def __init__(self, window_manager: Optional[object]) -> None:
        """
        Initializes the IconManager.

        Args:
            window_manager (Optional[object]): The WindowManager instance to control windows.
        """
        self.window_manager = window_manager
        self.icons = []
        self.window_icons = {}
        self.lock = threading.RLock()
        self.main_icon = None

    def set_main_icon(self, icon: pystray.Icon) -> None:
        """
        Sets the primary system tray icon.

        Args:
            icon (pystray.Icon): The main application tray icon.
        """
        self.main_icon = icon

    def get_icon_image(self, window_id: str) -> Image.Image:
        """
        Extracts the window icon image from a given window ID using xprop.

        Args:
            window_id (str): X11 window ID.

        Returns:
            Image.Image: The extracted icon image, or a default image on failure.
        """
        icon_path = f'/tmp/window_icon_{window_id}.png'
        try:
            result = subprocess.run(
                ['xprop', '-notype', '32c', '_NET_WM_ICON', '-id', window_id],
                capture_output=True, text=True, check=True
            )
            data = result.stdout.split('=')[1].strip().replace(',', '').split()
            if not data:
                return Image.open(DEFAULT_ICON)

            numbers = [int(x) for x in data]
            if len(numbers) < 2:
                return Image.open(DEFAULT_ICON)
            width, height = numbers[:2]
            pixel_data = numbers[2:]

            if len(pixel_data) != width * height:
                return Image.open(DEFAULT_ICON)

            rgba_data = [(p >> 16 & 0xFF, p >> 8 & 0xFF, p & 0xFF, p >> 24 & 0xFF) for p in pixel_data]
            img = Image.new('RGBA', (width, height))
            img.putdata(rgba_data)
            img.save(icon_path, 'PNG')
            return Image.open(icon_path) if os.path.exists(icon_path) else Image.open(DEFAULT_ICON)
        except Exception:
            return Image.open(DEFAULT_ICON)

    def create_tray_icon(self, window_id: str, window_name: str) -> None:
        """
        Creates a system tray icon for the specified window.

        Args:
            window_id (str): X11 window ID.
            window_name (str): Name of the window.
        """
        if window_id in self.window_icons:
            return

        image = self.get_icon_image(window_id)
        icon_name = f"window-{window_id}-{uuid.uuid4().hex}"

        menu = pystray.Menu(
            pystray.MenuItem(f'Restore "{window_name}"', lambda icon, _: self.restore_window(window_id)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f"Kill {window_name}", lambda icon, _: self.kill_window(window_id, window_name))
        )

        icon = pystray.Icon(icon_name, icon=image, title=window_name, menu=menu)

        with self.lock:
            self.icons.append(icon)
            self.window_icons[window_id] = icon

        threading.Thread(target=icon.run_detached, daemon=True).start()
        time.sleep(0.1)
        self.update_main_menu()

    def restore_window(self, window_id: str) -> None:
        """
        Restores a previously hidden window and removes its tray icon.

        Args:
            window_id (str): X11 window ID.
        """
        icon = self.window_icons[window_id]
        self.window_manager.toggle_window(window_id, True)
        self.remove_icon(icon, window_id)

    def kill_window(self, window_id: str, window_name: str) -> None:
        """
        Kills the specified window after confirmation and removes its tray icon.

        Args:
            window_id (str): X11 window ID.
            window_name (str): Name of the window.
        """
        icon = self.window_icons[window_id]
        self.window_manager.kill_window(window_id, window_name)
        self.remove_icon(icon, window_id)

    def remove_icon(self, icon: pystray.Icon, window_id: str) -> None:
        """
        Removes a tray icon associated with a window.

        Args:
            icon (pystray.Icon): The icon to remove.
            window_id (str): X11 window ID.
        """
        with self.lock:
            try:
                icon.visible = False
                icon.stop()
                self.icons.remove(icon)
                del self.window_icons[window_id]
                self.update_main_menu()
            except Exception as e:
                print(f"Failed to Remove Icon: {e}")

    def unhide_all(self) -> None:
        """
        Restores all hidden windows and removes their tray icons.
        """
        with self.lock:
            for window_id in list(self.window_icons.keys()):
                try:
                    self.restore_window(window_id)
                except Exception as e:
                    print(f"Failed Unhide All: {e}")

            self.window_icons.clear()
            self.icons.clear()

    def shutdown(self) -> None:
        """
        Shuts down the icon manager and restores all hidden windows.
        """
        self.unhide_all()

    def update_main_menu(self) -> None:
        """
        Updates the main tray icon's menu based on the current state.
        """
        if not self.main_icon:
            return

        menu_items = [
            pystray.MenuItem("Trayify Window", lambda icon, _: self.window_manager.select_window()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", lambda icon, _: self.window_manager.shutdown())
        ]

        if self.window_icons:
            menu_items.insert(1, pystray.MenuItem(f"Unhide All ({len(self.window_icons)})", lambda icon, _: self.unhide_all()))

        try:
            self.main_icon.menu = pystray.Menu(*menu_items)
            self.main_icon.update_menu()
        except Exception as e:
            print(f"Unable to create Main Icon: {e}")
