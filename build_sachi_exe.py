import os
import sys
import subprocess
from pathlib import Path

print("🧠 Building Sachi EXE...")

# Path to your main script
current_dir =  Path(__file__).parent
script_file = current_dir / "Shinpuru-Sachi.py"

if not script_file.exists():
    print("❌ Could not find Shinpuru-Sachi.py in this folder.")
    sys.exit(1)

# Output directory for the EXE
dist_dir = current_dir / "dist"
dist_dir.mkdir(exist_ok=True)

# PyInstaller command options:
# -y: overwrite
# --onefile: bundle into single exe
# --noconsole / --windowed: no terminal popup (optional)
# --icon: optional, specify an icon file
pyinstaller_cmd = [
    sys.executable,
    "-m", "PyInstaller",
    "--onefile",
    "--noconsole",  # remove this if you want terminal output
    "--distpath", str(dist_dir),
    "--name", "Sachi",
    str(script_file)
]

print("🔨 Running PyInstaller...")
subprocess.run(pyinstaller_cmd, check=True)
print("✅ EXE built successfully!")

exe_path = dist_dir / "Sachi.exe"
if exe_path.exists():
    print(f"🎉 Your EXE is ready at: {exe_path}")
    print("You can now copy it anywhere and run 'Sachi.exe -S \"who owns gpt\"'")
else:
    print("❌ EXE build failed. Check PyInstaller logs.")