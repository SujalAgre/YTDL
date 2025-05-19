import platform
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ascii_art import display_ascii
from core.utils import clear_screen
from core.video import download_video
from core.audio import download_audio
from core.playlists import download_playlist
from core.streams import show_all_streams
from core.channel import download_channel

def create_required_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs("YTDL", exist_ok=True)

def homepage():
    """Display the main menu and handle user choices."""
    while True:
        try:
            clear_screen()
            display_ascii("ytdl")

            
            print("---->> MAIN MENU <<----")
            
            print("\n-> 1. Download Video")
            print("-> 2. Download Audio")
            print("-> 3. Download Playlist")
            print("-> 4. Download Channel")
            print("-> 5. Show All Streams")
            print("-> 0. Exit")
         
            
            try:
                choice = int(input("\nEnter your choice [0-5]: "))
                if choice == 0:
                    clear_screen()
                    sys.exit(0)
                    
                match choice:
                    case 1: download_video()
                    case 2: download_audio()
                    case 3: download_playlist()
                    case 4: download_channel()
                    case 5: show_all_streams()
                    case _: 
                        print("Invalid choice. Please try again.")
                        input("Press Enter to continue...")
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                input("Press Enter to continue...")
            except Exception as e:
                print(f"An error occurred: {e}")
                input("Press Enter to continue...")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            input("Press Enter to continue...")

def main():
    """Main entry point of the application."""
    try:
        # Create required directories
        create_required_directories()
        
        # Start the application
        homepage()
        
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("\nThank you for using YTDL!")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()


def post_process():
    choice = input("Want to continue? [Y/N]: ").strip().lower()
    
    if choice == "y":
        clear_screen()
        homepage()
    else:
        return

