from pytubefix import YouTube
import os
import sys
import shutil

from core.utils import clear_screen, sanitize_filename, create_hidden_temp_dir
from ascii_art import display_ascii

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} GB"

def show_all_streams():
    from app import homepage

    while True:
        clear_screen()
        display_ascii("streams")
        print("---->> ALL STREAMS <<----")

        url = input("\nEnter video URL [0 to exit, 9 to go back]: ")
        
        if url == "0":
            clear_screen()
            sys.exit(0)
        elif url == "9":
            homepage()
            return

        try:
            yt = YouTube(url)

            # Display video details
            clear_screen()
            display_ascii("streams")

            print("---->> ALL STREAMS <<----")
            print(f"\nTitle: {yt.title}")
            print(f"Channel: {yt.author}")
            print(f"Length: {yt.length // 60} minutes {yt.length % 60} seconds")
            print("\nAvailable Streams:\n")

            # Get all available streams
            streams = yt.streams
            if not streams:
                print("No streams available for this video.")
                input("Press Enter to continue...")
                continue

            # Display stream information
            for stream in streams:
                stream_type = (
                    "Video+Audio" if stream.is_progressive else
                    "Video-only" if stream.includes_video_track and not stream.includes_audio_track else
                    "Audio-only"
                )
                resolution = stream.resolution or "---"
                abr = stream.abr or "---"
                mime = stream.mime_type or "---"
                filesize = format_size(stream.filesize) if stream.filesize else "---"

                print(f"itag: {stream.itag:<6} {stream_type:<12} {resolution:<10} {abr:<10} {mime:<12} {filesize:<10}")

            # Get user choice
            try:
                itag = int(input("\nEnter [itag] of the stream (0 to exit, 9 to go back): "))
                if itag == 0:
                    clear_screen()
                    sys.exit(0)
                elif itag == 9:
                    homepage()
                    return
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                continue

            # Create required directories
            os.makedirs("YTDL", exist_ok=True)
            temp_dir = create_hidden_temp_dir()

            try:
                # Download the selected stream
                stream = yt.streams.get_by_itag(itag)
                if not stream:
                    print("Error: Stream not found!")
                    return

                # Create downloads directory if it doesn't exist
                os.makedirs("YTDL", exist_ok=True)

                # Download the stream
                print(f"\nDownloading: {yt.title} | itag: {itag}")
                safe_title = sanitize_filename(yt.title)
                file_extension = stream.mime_type.split('/')[-1]
                output_path = stream.download(
                    filename=f"{safe_title}.{file_extension}",
                    output_path="YTDL"
                )

                # print(f"\nDownload complete: {output_path}")
                print(f"\nDownload complete!")
                input("\nPress Enter to continue...")
                homepage()
                return

            except Exception as e:
                print(f"An error occurred: {e}")
                input("Press Enter to continue...")

            finally:
                # Clean up temp directory
                try:
                    shutil.rmtree("temp")
                except:
                    pass

        except Exception as e:
            print(f"An error occurred: {e}")
            input("Press Enter to continue...")
