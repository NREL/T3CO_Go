import os
import sys
import subprocess
import platform

def build_executable():
    # Determine the platform
    current_platform = platform.system()
    
    # Define the command to build the executable
    if current_platform == "Windows":
        command = ["pyinstaller", "--onefile", "manage.py"]
    elif current_platform == "Darwin":  # macOS
        command = ["pyinstaller", "--onefile", "manage.py"]
    else:
        print("Unsupported platform. This script only supports Windows and macOS.")
        sys.exit(1)

    # Run the command
    try:
        subprocess.run(command, check=True)
        print("Executable built successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while building the executable: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()