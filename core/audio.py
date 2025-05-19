from pytubefix import YouTube
import os, subprocess, shutil
import sys

from core.utils import clear_screen, sanitize_filename, get_ffmpeg_path, create_hidden_temp_dir
from ascii_art import display_ascii

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} GB"

def download_audio():
    from app import homepage

    while True:
        clear_screen()
        display_ascii("audio")

        print("---->> DOWNLOAD AUDIO <<----")

        print("\n-> 1: Download MP3 Audio [Smaller File Size]")
        print("-> 2: Download WAV Audio [Higher Quality]")
        print("\n-> 9: Back to Homepage")
        print("-> 0: Exit")
        
        try:
            choice = int(input("\nEnter your choice [0-2, 9]: "))
            
            if choice == 0:
                clear_screen()
                sys.exit(0)
            elif choice == 9:
                homepage()
                return
                
            if choice not in [1, 2]:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                continue

            clear_screen()
            display_ascii("audio")
            
            url = input("Enter video URL [0 to exit, 9 to go back]: ")
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
            print(f"Title: {yt.title}")
            print(f"Channel: {yt.author}")
            print(f"Length: {yt.length // 60} minutes {yt.length % 60} seconds")
            print("\nSelected Stream:")
            
            # Get highest quality audio stream
            stream = yt.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()
            if not stream:
                print("No suitable audio stream found.")
                input("Press Enter to continue...")
                return

            print(f"Audio: {stream.abr} ({format_size(stream.filesize)})")
            print(f"Format: {'MP3' if choice == 1 else 'WAV'}")
            
            proceed = input("\nProceed with download? (y/n): ").lower()
            if proceed != 'y':
                return

            # Create required directories
            os.makedirs("YTDL", exist_ok=True)
            os.makedirs("temp", exist_ok=True)

            try:
                # Create audio folder
                safe_title = sanitize_filename(yt.title)
                audio_path = os.path.join("YTDL", f"Audio [{'MP3' if choice == 1 else 'WAV'}] [{safe_title}]")
                os.makedirs(audio_path, exist_ok=True)

                # Download WEBM audio
                print("\nDownloading audio...")
                temp_path = stream.download(filename='audio_temp.webm', output_path=audio_path)

                if choice == 1:
                    # Convert to MP3
                    output_path = os.path.join(audio_path, f"{safe_title}.mp3")
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
                    output_path = os.path.join(audio_path, f"{safe_title}.wav")
                    command = [
                        get_ffmpeg_path(),
                        "-hide_banner",
                        "-loglevel", "error",
                        "-i", temp_path,
                        "-vn",  # No video
                        "-acodec", "pcm_s16le",  # PCM 16-bit encoding
                        "-ar", "44100",          # 44.1kHz sample rate
                        "-ac", "2",              # Stereo
                        "-y",  # Overwrite output file if exists
                        output_path
                    ]

                try:
                    subprocess.run(command, check=True, stderr=subprocess.DEVNULL)
                    print(f"\nDownload complete! {yt.title} saved in YTDL folder")   
                except subprocess.CalledProcessError as e:
                    print(f"Error during conversion: {e}")
                    # Try alternative conversion method
                    try:
                        print("Trying alternative conversion method...")
                        alt_command = [
                            get_ffmpeg_path(),
                            "-hide_banner",
                            "-loglevel", "error",
                            "-i", temp_path,
                            "-vn",  # No video
                            "-acodec", "libmp3lame" if choice == 1 else "pcm_s16le",
                            "-ar", "44100",
                            "-ac", "2",
                            "-y",
                            output_path
                        ]
                        subprocess.run(alt_command, check=True, stderr=subprocess.DEVNULL)
                        print(f"\nDownload complete! {yt.title} saved in YTDL folder")
                    except subprocess.CalledProcessError as e:
                        print(f"Error during alternative conversion: {e}")
                finally:
                    # Clean up temporary file
                    try:
                        os.remove(temp_path)
                    except:
                        pass

            finally:
                # Clean up temp directory
                try:
                    shutil.rmtree("temp")
                except:
                    pass

            input("\nPress Enter to continue...")
            continue

        except ValueError:
            print("Please enter a valid number.")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"An error occurred: {e}")
            input("Press Enter to continue...")
