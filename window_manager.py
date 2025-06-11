import subprocess
import sys
from typing import Tuple
from typing import Optional

class WindowManager:
    """
    Manages window operations such as selecting, toggling visibility,
    and terminating windows on X11 environments.
    """

    def __init__(self, icon_manager: Optional[object]) -> None:
        """
        Initializes the WindowManager.

        Args:
            icon_manager (IconManager): Reference to the associated IconManager.
        """
        self.icon_manager = icon_manager

    def select_window(self) -> None:
        """
        Opens a window selection dialog using 'xwininfo', creates a tray icon
        for the selected window, and hides the window from view.
        """
        window_id, window_name = self.get_window_info()
        self.icon_manager.create_tray_icon(window_id, window_name)
        self.toggle_window(window_id, show=False)

    def get_window_info(self) -> Tuple[str, str]:
        """
        Runs 'xwininfo' to let the user select a window and parses its window ID and name.

        Returns:
            Tuple[str, str]: A tuple containing the window ID and window name.

        Raises:
            Exception: If window info cannot be obtained or parsed.
        """
        try:
            result = subprocess.run(['xwininfo'], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                if "Window id:" in line:
                    parts = line.split(":")[2].strip()
                    window_id = parts.split(" ")[0].strip()
                    window_name = parts[len(window_id):].strip().strip('"')
                    return window_id, window_name
            raise Exception("No window ID found")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get window info: {e}")

    def toggle_window(self, window_id: str, show: bool = False) -> None:
        """
        Shows or hides the specified window using 'xdotool'.

        Args:
            window_id (str): The window ID to toggle.
            show (bool, optional): Whether to show (True) or hide (False) the window. Defaults to False.

        Raises:
            Exception: If toggling the window fails.
        """
        try:
            action = 'windowmap' if show else 'windowunmap'
            subprocess.run(['xdotool', action, window_id], check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to toggle window: {e}")

    def kill_window(self, window_id: str, window_name: str) -> bool:
        """
        Prompts the user for confirmation and kills the specified window if confirmed.

        Args:
            window_id (str): The window ID to kill.
            window_name (str): The window name to display in the confirmation dialog.

        Returns:
            bool: True if the window was killed, False otherwise.

        Raises:
            Exception: If the kill operation fails.
        """
        try:
            result = subprocess.run(
                ['zenity', '--question', '--text', f'Are you sure you want to Terminate {window_name}?'],
                capture_output=True, text=True, check=True
            )
            if result.returncode == 0:
                subprocess.run(['xdotool', 'windowkill', window_id], check=True)
                return True
            return False
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to kill window: {e}")

    def shutdown(self) -> None:
        """
        Shuts down the WindowManager and associated IconManager, then exits the program.
        """
        self.icon_manager.shutdown()
        sys.exit(0)
