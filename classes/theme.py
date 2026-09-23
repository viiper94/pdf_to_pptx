import sys


def get_system_theme():
    """
    Detects the system's color theme on Windows and macOS.
    Returns 'dark' or 'light'. Defaults to 'dark' on other platforms or on error.
    """
    if sys.platform == 'win32':
        try:
            import winreg
            key_path = r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                return 'light' if value == 1 else 'dark'
        except (ImportError, FileNotFoundError, OSError):
            # Fallback if winreg fails or key doesn't exist
            return 'dark'

    elif sys.platform == 'darwin':  # macOS
        try:
            import subprocess
            cmd = 'defaults read -g AppleInterfaceStyle'
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, _ = p.communicate()
            # If the command returns 'Dark', it's dark mode. Otherwise, it's light.
            return 'dark' if stdout.decode().strip() == 'Dark' else 'light'
        except Exception:
            # Fallback on any error
            return 'dark'

    # Default for Linux and other platforms
    return 'dark'
