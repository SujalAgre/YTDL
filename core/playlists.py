import os, subprocess, shutil
import sys
from pytubefix import Playlist, YouTube

from core.utils import clear_screen, sanitize_filename, get_ffmpeg_path, create_hidden_temp_dir, format_size
from ascii_art import display_ascii
from core.colors import white, red, light_green

def download_playlist():
    from app import homepage

    while True:
        clear_screen()
        display_ascii("playlist")

        print(white("---=>> DOWNLOAD PLAYLIST <<=---"))

        print(white("\n-> 1: Download Videos"))
        print(white("-> 2: Download Audio"))
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
            display_ascii("playlist")

            print(white("---=>> DOWNLOAD PLAYLIST <<=---"))
            
            url = input(white("\nEnter playlist URL [0 to exit, 9 to go back]: "))
            if url == "0":
                clear_screen()
                sys.exit(0)
            elif url == "9":
                homepage()
                return

            playlist = Playlist(url)

            # Get playlist details
            clear_screen()
            display_ascii("playlist")
            print(white(f"Playlist: {playlist.title}"))
            print(white(f"Channel: {playlist.owner}"))
            print(white(f"Total Videos: {len(playlist.video_urls)}"))
            
            if choice == 1:
                print(white("\nSelected Format: MP4 Video"))
                # Get sample streams from first video for size estimation
                first_video = YouTube(playlist.video_urls[0])
                video_stream = first_video.streams.filter(only_video=True, file_extension='mp4').order_by('resolution').desc().first()
                audio_stream = first_video.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()
                if video_stream and audio_stream:
                    avg_size = (video_stream.filesize + audio_stream.filesize) * len(playlist.video_urls)
                    print(white(f"Estimated Total Size: {format_size(avg_size)}"))
            else:  # choice == 2
                # Audio format submenu
                clear_screen()
                display_ascii("audio")

                print(white("---=>> SELECT AUDIO FORMAT <<=---"))

                print(white("\n-> 1: MP3 Audio [Smaller File Size]"))
                print(white("-> 2: WAV Audio [Higher Quality]"))
                print(white("\n-> 9: Back to Homepage"))
                print(white("-> 0: Exit"))
                
                audio_choice = int(input(white("\nEnter your choice [0-2, 9]: ")))
                if audio_choice == 0:
                    clear_screen()
                    sys.exit(0)
                elif audio_choice == 9:
                    homepage()
                    return
                if audio_choice not in [1, 2]:
                    print(red("Invalid choice. Please try again."))
                    input(white("Press Enter to continue..."))
                    return
                
                print(white(f"\nSelected Format: {'MP3' if audio_choice == 1 else 'WAV'} Audio"))
                # Get sample stream from first video for size estimation
                first_video = YouTube(playlist.video_urls[0])
                audio_stream = first_video.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()
                if audio_stream:
                    avg_size = audio_stream.filesize * len(playlist.video_urls)
                    print(white(f"Estimated Total Size: {format_size(avg_size)}"))
            
            proceed = input(white("\nProceed with download? (y/n): ")).lower()
            if proceed != 'y':
                return

            # Create required directories
            os.makedirs("YTDL", exist_ok=True)
            os.makedirs("temp", exist_ok=True)

            try:
                # Create playlist folder
                safe_playlist_name = sanitize_filename(playlist.title)
                
                if choice == 1:
                    folder_name = f"Videos [{safe_playlist_name}]"
                else:  # choice == 2
                    folder_name = f"Audio [{'MP3' if audio_choice == 1 else 'WAV'}] [{safe_playlist_name}]"
                
                playlist_path = os.path.join("YTDL", folder_name)
                os.makedirs(playlist_path, exist_ok=True)

                total_videos = len(playlist.video_urls)
                print(white(f"\nFound {total_videos} videos in playlist"))

                for i, video_url in enumerate(playlist.video_urls, 1):
                    try:
                        yt = YouTube(video_url)
                        safe_title = sanitize_filename(yt.title)
                        
                        print(white(f"\nProcessing video {i}/{total_videos}: {yt.title}"))

                        if choice == 1:
                            # Get highest resolution video-only stream
                            video_stream = yt.streams.filter(only_video=True, file_extension='mp4').order_by('resolution').desc().first()
                            if not video_stream:
                                print(red("No suitable video stream found."))
                                continue

                            # Get highest quality audio-only stream
                            audio_stream = yt.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()
                            if not audio_stream:
                                print(red("No suitable audio stream found."))
                                continue

                            # Download paths
                            video_path = video_stream.download(filename='video_temp.mp4', output_path='temp')
                            audio_path = audio_stream.download(filename='audio_temp.webm', output_path='temp')

                            # Set output path
                            output_path = os.path.join(playlist_path, f"{safe_title}.mp4")

                            # Merge using FFmpeg
                            command = [
                                get_ffmpeg_path(),
                                "-hide_banner",
                                "-loglevel", "error",
                                "-i", video_path,
                                "-i", audio_path,
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
                                print(light_green(f"Downloaded {yt.title} in YTDL folder"))
                            except subprocess.CalledProcessError as e:
                                print(red(f"Error occurred during merge: {e}"))
                            finally:
                                # Clean up temporary files
                                try:
                                    os.remove(video_path)
                                    os.remove(audio_path)
                                except:
                                    pass

                        else:  # choice == 2
                            # Get highest quality audio stream
                            stream = yt.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()
                            if not stream:
                                print(red("No suitable audio stream found."))
                                continue

                            # Download WEBM audio
                            temp_path = stream.download(filename='audio_temp.webm', output_path='temp')

                            if audio_choice == 1:
                                # Convert to MP3
                                output_path = os.path.join(playlist_path, f"{safe_title}.mp3")
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
                            else:  # audio_choice == 2
                                # Convert to WAV
                                output_path = os.path.join(playlist_path, f"{safe_title}.wav")
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
                                print(light_green(f"Downloaded {yt.title} in YTDL folder"))
                            except subprocess.CalledProcessError as e:
                                print(red(f"Error during conversion: {e}"))
                                # Try alternative conversion method
                                try:
                                    print(white("Trying alternative conversion method..."))
                                    alt_command = [
                                        get_ffmpeg_path(),
                                        "-hide_banner",
                                        "-loglevel", "error",
                                        "-i", temp_path,
                                        "-vn",  # No video
                                        "-acodec", "libmp3lame" if audio_choice == 1 else "pcm_s16le",
                                        "-ar", "44100",
                                        "-ac", "2",
                                        output_path
                                    ]
                                    subprocess.run(alt_command, check=True, stderr=subprocess.DEVNULL)
                                    print(light_green(f"Downloaded {yt.title} in YTDL folder"))
                                except subprocess.CalledProcessError as e:
                                    print(red(f"Error during alternative conversion: {e}"))
                            finally:
                                # Clean up temporary file
                                try:
                                    os.remove(temp_path)
                                except:
                                    pass

                    except Exception as e:
                        print(red(f"Error processing video: {e}"))
                        continue

                print(light_green("\nPlaylist download complete!"))

            finally:
                # Clean up temp directory
                try:
                    shutil.rmtree("temp")
                except:
                    pass

            input(white("Press Enter to continue..."))
            continue

        except ValueError:
            print(red("Please enter a valid number."))
            input(white("Press Enter to continue..."))
        except Exception as e:
            print(red(f"An error occurred: {e}"))
            input(white("Press Enter to continue..."))

