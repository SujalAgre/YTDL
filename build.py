import PyInstaller.__main__
import os
import sys
from pathlib import Path

# Get the current directory
current_dir = Path(__file__).parent.absolute()

# Create required directories
os.makedirs("YTDL", exist_ok=True)
os.makedirs("temp", exist_ok=True)

# Determine the separator for the OS
separator = ';' if sys.platform == 'win32' else ':'

# Define data files to include
data_files = [
    ('ffmpeg.exe', '.'),  # Include FFMPEG in the root directory
    ('core', 'core'),
    ('ascii_art.py', '.'),
    ('YTDL', 'YTDL'),  # Include YTDL directory
    ('temp', 'temp'),  # Include temp directory
]

# Convert data files to PyInstaller format
add_data_args = [f'--add-data={src}{separator}{dst}' for src, dst in data_files]

PyInstaller.__main__.run([
    'app.py',  # Your main script
    '--onefile',  # Create a single executable
    '--name=YTDL',  # Name of the executable
    '--console',  # Show console window (needed for CLI)
    '--clean',  # Clean PyInstaller cache
    '--noconfirm',  # Replace existing build without asking
    *add_data_args,  # Add all data files
    '--add-binary=ffmpeg.exe;.',  # Add FFMPEG as a binary in root directory
])