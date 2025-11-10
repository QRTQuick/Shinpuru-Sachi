import os
import shutil
import sys
import winreg
import ctypes
import urllib.request
from pathlib import Path

# === Configuration ===
DOWNLOAD_URL = "https://github.com/QRTQuick/Shinpuru-Sachi/raw/main/dist/Sachi.exe"  # ✅ Direct link to .exe file
FILE_NAME = "Sachi.exe"

# --- Check for admin privileges ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("⚠️ Administrator privileges are required to modify PATH system-wide.")
    print("Attempting to relaunch as admin...")
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(f'"{arg}"' for arg in sys.argv), None, 1
    )
    sys.exit(0)

print("🧠 Sachi Installer (Running as Administrator)")
print("============================================")
print("This installer will:")
print("1. Create a folder at: C:\\Users\\<you>\\SachiTools")
print("2. Download the latest Sachi.exe")
print("3. Create a launcher (Sachi.bat)")
print("4. Add SachiTools to your PATH (so you can type 'Sachi' anywhere)\n")

confirm = input("Do you want to continue? (y/n): ").strip().lower()
if confirm != "y":
    print("❌ Installation cancelled by user.")
    sys.exit(0)

# --- Setup paths ---
user = os.getlogin()
sachi_dir = Path(f"C:/Users/{user}/SachiTools")
sachi_exe = sachi_dir / FILE_NAME
sachi_bat = sachi_dir / "Sachi.bat"

# --- Create SachiTools folder ---
os.makedirs(sachi_dir, exist_ok=True)

# --- Download latest exe ---
print("⬇️ Downloading latest Sachi.exe ...")
try:
    urllib.request.urlretrieve(DOWNLOAD_URL, sachi_exe)
    print(f"✅ Downloaded to {sachi_exe}")
except Exception as e:
    print(f"❌ Failed to download file: {e}")
    sys.exit(1)

# --- Create launcher ---
bat_content = f'@echo off\n"{sachi_exe}" %*\n'
with open(sachi_bat, "w") as f:
    f.write(bat_content)
print("✅ Created Sachi.bat launcher")

# --- Add to PATH ---
def add_to_path(dir_path):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE,
        )
        try:
            current_path, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current_path = ""
        if dir_path not in current_path:
            new_path = current_path + (";" if current_path else "") + dir_path
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✅ Added {dir_path} to PATH. (Restart terminal to apply)")
        else:
            print(f"ℹ️ {dir_path} already in PATH.")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"❌ Failed to edit PATH: {e}")

add_to_path(str(sachi_dir))

print("\n🎉 Installation complete!")
print("Now open a NEW terminal and type:")
print('  Sachi -S "who owns stackcheckmate"')