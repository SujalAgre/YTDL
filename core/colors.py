"""Color utilities for terminal output."""

# ANSI color codes
WHITE = '\033[97m'
RED = '\033[91m'
GREEN = '\033[92m'
LIGHT_GREEN = '\033[92m' 
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'

def white(text):
    """Return text in white color."""
    return f"{WHITE}{text}{RESET}"

def red(text):
    """Return text in red color."""
    return f"{RED}{text}{RESET}"

def green(text):
    """Return text in green color."""
    return f"{GREEN}{text}{RESET}"

def light_green(text):
    """Return text in light green color."""
    return f"{LIGHT_GREEN}{text}{RESET}"

def yellow(text):
    """Return text in yellow color."""
    return f"{YELLOW}{text}{RESET}"

def blue(text):
    """Return text in blue color."""
    return f"{BLUE}{text}{RESET}"

def magenta(text):
    """Return text in magenta color."""
    return f"{MAGENTA}{text}{RESET}"

def cyan(text):
    """Return text in cyan color."""
    return f"{CYAN}{text}{RESET}" 