import winreg
import os

def get_gta_path_from_registry():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\RAGE-MP") as key:
            path, _ = winreg.QueryValueEx(key, "GTAPath")
            if os.path.isdir(path):
                return path
    except FileNotFoundError:
        pass
    return None