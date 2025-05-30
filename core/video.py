from pytubefix import YouTube
import os, subprocess, shutil
import sys

from core.utils import clear_screen, sanitize_filename, get_ffmpeg_path, create_hidden_temp_dir, format_size
from ascii_art import display_ascii
from core.colors import white, red, light_green

def download_video():
    from app import homepage

    while True:
        clear_screen()
        display_ascii("video")

        print(white("---=>> DOWNLOAD VIDEO <<=---"))
        
        url = input(white("\nEnter video URL [0 to exit, 9 to go back]: "))
        
        if url == "0":
            clear_screen()
            sys.exit(0)
        elif url == "9":
            homepage()
            return
            
        try:
            yt = YouTube(url)

            # Get video details
            clear_screen()
            display_ascii("video")
            print(white(f"Title: {yt.title}"))
            print(white(f"Channel: {yt.author}"))
            print(white(f"Length: {yt.length // 60} minutes {yt.length % 60} seconds"))
            print(white("\nSelected Streams:"))
            
            # Get highest resolution video-only stream
            video_stream = yt.streams.filter(only_video=True, file_extension='mp4').order_by('resolution').desc().first()
            if not video_stream:
                print(red("No suitable video stream found."))
                input(white("Press Enter to continue..."))
                continue

            # Get highest quality audio-only stream
            audio_stream = yt.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()
            if not audio_stream:
                print(red("No suitable audio stream found."))
                input(white("Press Enter to continue..."))
                continue

            print(white(f"Video: {video_stream.resolution} ({format_size(video_stream.filesize)})"))
            print(white(f"Audio: {audio_stream.abr} ({format_size(audio_stream.filesize)})"))
            print(white(f"Total Size: {format_size(video_stream.filesize + audio_stream.filesize)}"))
            
            proceed = input(white("\nProceed with download? (y/n): ")).lower()
            if proceed != 'y':
                continue

            # Create required directories
            os.makedirs("YTDL", exist_ok=True)
            temp_dir = create_hidden_temp_dir()

            try:
                # Download paths
                print(white("\nDownloading video..."))
                video_temp = video_stream.download(filename='video_temp.mp4', output_path=temp_dir)
                audio_temp = audio_stream.download(filename='audio_temp.webm', output_path=temp_dir)

                # Set output path
                safe_title = sanitize_filename(yt.title)
                output_path = os.path.join("YTDL", f"{safe_title}.mp4")

                # Merge using FFmpeg
                command = [
                    get_ffmpeg_path(),
                    "-hide_banner",
                    "-loglevel", "error",
                    "-i", video_temp,
                    "-i", audio_temp,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",  # Set audio bitrate
                    "-ar", "44100",  # Set audio sample rate
                    "-strict", "experimental",
                    "-y",  # Overwrite output file if exists
                    output_path
                ]
                
                try:
                    subprocess.run(command, check=True, stderr=subprocess.DEVNULL)
                    print(light_green(f"\nDownload complete! {yt.title} saved in YTDL folder"))
                except subprocess.CalledProcessError as e:
                    print(red(f"Error occurred during merge: {e}"))
                finally:
                    # Clean up temporary files
                    try:
                        os.remove(video_temp)
                        os.remove(audio_temp)
                    except:
                        pass

            finally:
                # Clean up temp directory
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass

            input(white("\nPress Enter to continue..."))
            continue

        except ValueError:
            print(red("Please enter a valid URL."))
            input(white("Press Enter to continue..."))
        except Exception as e:
            print(red(f"An error occurred: {e}"))
            input(white("Press Enter to continue..."))

