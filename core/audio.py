from pytubefix import YouTube
import os, subprocess, shutil
import sys

from core.utils import clear_screen, sanitize_filename, get_ffmpeg_path, create_hidden_temp_dir, format_size
from ascii_art import display_ascii
from core.colors import white, red, light_green

def download_audio():
    from app import homepage

    while True:
        clear_screen()
        display_ascii("audio")

        print(white("---=>> DOWNLOAD AUDIO <<=---"))

        print(white("\n-> 1: Download MP3 Audio [Smaller File Size]"))
        print(white("-> 2: Download WAV Audio [Higher Quality]"))
        print(white("\n-> 9: Back to Homepage"))
        print(white("-> 0: Exit"))
        
        try:
            choice = int(input(white("\nEnter your choice [0-2, 9]: ")))
            
            if choice == 0:
                clear_screen()
                sys.exit(0)
            elif choice == 9:
                homepage()
                return
                
            if choice not in [1, 2]:
                print(red("Invalid choice. Please try again."))
                input(white("Press Enter to continue..."))
                continue

            clear_screen()
            display_ascii("audio")
            
            url = input(white("Enter video URL [0 to exit, 9 to go back]: "))
            if url == "0":
                clear_screen()
                sys.exit(0)
            elif url == "9":
                homepage()
                return

            yt = YouTube(url)

            # Get audio details
            clear_screen()
            display_ascii("audio")
            print(white(f"Title: {yt.title}"))
            print(white(f"Channel: {yt.author}"))
            print(white(f"Length: {yt.length // 60} minutes {yt.length % 60} seconds"))
            print(white("\nSelected Stream:"))
            
            # Get highest quality audio stream
            stream = yt.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()
            if not stream:
                print(red("No suitable audio stream found."))
                input(white("Press Enter to continue..."))
                return

            print(white(f"Audio: {stream.abr} ({format_size(stream.filesize)})"))
            print(white(f"Format: {'MP3' if choice == 1 else 'WAV'}"))
            
            proceed = input(white("\nProceed with download? (y/n): ")).lower()
            if proceed != 'y':
                return

            # Create required directories
            os.makedirs("YTDL", exist_ok=True)
            os.makedirs("temp", exist_ok=True)

            try:
                safe_title = sanitize_filename(yt.title)
                temp_dir = create_hidden_temp_dir()

                # Download WEBM audio
                print(white("\nDownloading audio..."))
                temp_path = stream.download(filename='audio_temp.webm', output_path=temp_dir)

                if choice == 1:
                    output_path = os.path.join("YTDL", f"{safe_title}.mp3")
                    command = [
                        get_ffmpeg_path(),
                        "-hide_banner",
                        "-loglevel", "error",
                        "-i", temp_path,
                        "-vn",  # No video
                        "-acodec", "libmp3lame",  # Use LAME MP3 encoder
                        "-qscale:a", "0",          # Highest quality (VBR)
                        "-ar", "44100",           # Set audio sample rate
                        "-ac", "2",               # Stereo
                        "-y",  # Overwrite output file if exists
                        output_path
                    ]
                else:  # choice == 2
                    # Convert to WAV
                    output_path = os.path.join("YTDL", f"{safe_title}.wav")
                    command = [
                        get_ffmpeg_path(),
                        "-hide_banner",
                        "-loglevel", "error",
                        "-i", temp_path,
                        "-vn",  # No video
                        "-acodec", "pcm_s16le",  # Use PCM WAV encoder
                        "-ar", "44100",          # Set audio sample rate
                        "-ac", "2",              # Stereo
                        "-y",  # Overwrite output file if exists
                        output_path
                    ]

                try:
                    subprocess.run(command, check=True, stderr=subprocess.DEVNULL)
                    print(light_green(f"\nDownload complete! {yt.title} saved in YTDL folder"))
                except subprocess.CalledProcessError as e:
                    print(red(f"Error during conversion: {e}"))
                finally:
                    try:
                        os.remove(temp_path)
                    except:
                        pass
            finally:
                try:
                    shutil.rmtree("temp")
                except:
                    pass

            input(white("\nPress Enter to continue..."))
            continue

        except ValueError:
            print(red("Please enter a valid number."))
            input(white("Press Enter to continue..."))
        except Exception as e:
            print(red(f"An error occurred: {e}"))
            input(white("Press Enter to continue..."))
