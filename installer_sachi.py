import os
import shutil
import sys
import winreg
from pathlib import Path

print("🧠 Sachi Installer")
print("==================")
print("This installer will:")
print("1. Create a folder at: C:\\Users\\<you>\\SachiTools")
print("2. Copy Shinpuru-Sachi.py there")
print("3. Create a launcher (Sachi.bat)")
print("4. Add SachiTools to your PATH (so you can type 'Sachi' anywhere)\n")

confirm = input("Do you want to continue? (y/n): ").strip().lower()
if confirm != "y":
    print("❌ Installation cancelled by user.")
    sys.exit(0)

# --- Setup paths ---
user = os.getlogin()
sachi_dir = Path(f"C:/Users/{user}/SachiTools")
sachi_py = sachi_dir / "Shinpuru-Sachi.py"
sachi_bat = sachi_dir / "Sachi.bat"

# --- Create SachiTools folder ---
os.makedirs(sachi_dir, exist_ok=True)

# --- Copy your script there (assuming it's in same folder as installer) ---
current_dir = Path(__file__).parent
src_script = current_dir / "Shinpuru-Sachi.py"
if not src_script.exists():
    print("❌ Could not find Shinpuru-Sachi.py in this folder.")
    sys.exit(1)

shutil.copy2(src_script, sachi_py)
print(f"✅ Copied Shinpuru-Sachi.py to {sachi_dir}")

# --- Create the launcher .bat file ---
bat_content = f'@echo off\npython "{sachi_py}" %*\n'
with open(sachi_bat, "w") as f:
    f.write(bat_content)
print("✅ Created Sachi.bat launcher")

# --- Add SachiTools to PATH (user variable) ---
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
print('  Sachi -S "who owns gpt"')