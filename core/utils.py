import os
import sys
from pathlib import Path
import platform
import subprocess

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

def get_ffmpeg_path():
    """Get the path to FFmpeg executable."""
    try:
        # If running as bundled executable
        if getattr(sys, 'frozen', False):
            # Get the directory where the executable is located
            base_path = Path(sys._MEIPASS)
        else:
            # Get the directory where the script is located
            base_path = Path(__file__).parent.parent

        # Look for ffmpeg.exe in the base path
        ffmpeg_path = base_path / "ffmpeg.exe"
        
        if ffmpeg_path.exists():
            return str(ffmpeg_path)
        
        # Fallback to system FFMPEG if not found
        return "ffmpeg"
    except Exception:
        # Fallback to system FFMPEG if any error occurs
        return "ffmpeg"

def create_hidden_temp_dir():
    """Create a temp directory."""
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir
