from pytubefix import Channel, YouTube
import os, subprocess, shutil
import sys
import re

from core.utils import clear_screen, sanitize_filename, get_ffmpeg_path
from ascii_art import display_ascii

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} GB"

def get_channel_info(url):
    """Get channel information from URL"""
    try:
        # Get channel info
        channel = Channel(url)
        channel_name = channel.channel_name
        return channel, channel_name
    except Exception as e:
        print(f"Error getting channel info: {e}")
        return None, None

def download_channel():
    from app import homepage

    while True:
        clear_screen()
        display_ascii("channel")

        print("---->> DOWNLOAD CHANNEL <<----")

        print("\n-> 1: Download Videos")
        print("-> 2: Download Audio")
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
            display_ascii("channel")

            print("---->> DOWNLOAD CHANNEL <<----")
            
            print("\nSupported formats:")
            print("\n-> https://www.youtube.com/c/ChannelName")
            print("-> https://www.youtube.com/channel/ChannelID")
            print("-> https://www.youtube.com/@ChannelName")
            channel_url = input("\nEnter channel URL [0 to exit, 9 to go back]: ")
            
            if channel_url == "0":
                clear_screen()
                sys.exit(0)
            elif channel_url == "9":
                homepage()
                return

            try:
                # Get channel info
                print("\nFetching channel info...")
                channel, channel_name = get_channel_info(channel_url)
                
                if not channel or not channel_name:
                    raise Exception("Could not get channel information")
                
                # Get all video URLs
                print("Fetching videos...")
                video_urls = []
                try:
                    # Get all videos from the channel
                    for video in channel.videos:
                        if hasattr(video, 'watch_url'):
                            video_urls.append(video.watch_url)
                            print(".", end="", flush=True)
                    print("\n")
                except Exception as e:
                    print(f"\nError fetching videos: {e}")
                    raise
                
                if not video_urls:
                    raise Exception("No videos found in this channel")
                
            except Exception as e:
                print(f"Error: {e}")
                print("\nMake sure you entered a valid channel URL.")
                input("Press Enter to continue...")
                continue

            # Get channel details
            clear_screen()
            display_ascii("channel")

            print("---->> DOWNLOAD CHANNEL <<----")
            
            print(f"\nChannel: {channel_name}")
            print(f"Total Videos: {len(video_urls)}")
            
            if choice == 1:
                print("\nSelected Format: MP4 Video")
                # Get sample streams from first video for size estimation
                try:
                    first_video = YouTube(video_urls[0])
                    video_stream = first_video.streams.filter(only_video=True, file_extension='mp4').order_by('resolution').desc().first()
                    audio_stream = first_video.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()
                    if video_stream and audio_stream:
                        avg_size = (video_stream.filesize + audio_stream.filesize) * len(video_urls)
                        print(f"Estimated Total Size: {format_size(avg_size)}")
                except:
                    print("Could not estimate total size.")
            else:  # choice == 2
                # Audio format submenu
                clear_screen()
                display_ascii("channel")

                print("---->> SELECT AUDIO FORMAT <<----")

                print("\n-> 1: MP3 Audio [Smaller File Size]")
                print("-> 2: WAV Audio [Higher Quality]")
                print("\n-> 9: Back to Homepage")
                print("-> 0: Exit")
                
                audio_choice = int(input("\nEnter your choice [0-2, 9]: "))
                if audio_choice == 0:
                    clear_screen()
                    sys.exit(0)
                elif audio_choice == 9:
                    homepage()
                    return
                if audio_choice not in [1, 2]:
                    print("Invalid choice. Please try again.")
                    input("Press Enter to continue...")
                    return
                
                clear_screen()
                display_ascii("channel")

                print("---->> SELECT AUDIO FORMAT <<----")
                
                print(f"\nSelected Format: {'MP3' if audio_choice == 1 else 'WAV'} Audio")
                # Get sample stream from first video for size estimation
                try:
                    first_video = YouTube(video_urls[0])
                    audio_stream = first_video.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()
                    if audio_stream:
                        avg_size = audio_stream.filesize * len(video_urls)
                        print(f"Estimated Total Size: {format_size(avg_size)}")
                except:
                    print("Could not estimate total size.")
            
            proceed = input("\nProceed with download? (y/n): ").lower()
            if proceed != 'y':
                return

            # Create required directories
            os.makedirs("YTDL", exist_ok=True)
            os.makedirs("temp", exist_ok=True)

            try:
                # Create channel folder
                safe_channel_name = sanitize_filename(channel_name)
                
                if choice == 1:
                    folder_name = f"{safe_channel_name} [Videos]"
                else:  # choice == 2
                    folder_name = f"{safe_channel_name} [Audio] [{'MP3' if audio_choice == 1 else 'WAV'}]"
                
                channel_path = os.path.join("YTDL", folder_name)
                os.makedirs(channel_path, exist_ok=True)

                total_videos = len(video_urls)
                print(f"\nFound {total_videos} videos in channel")

                for index, video_url in enumerate(video_urls, 1):
                    try:
                        if not isinstance(video_url, str):
                            print(f"Skipping invalid video URL at index {index}")
                            continue

                        yt = YouTube(video_url)
                        safe_title = sanitize_filename(yt.title)
                        print(f"\nDownloading {index}/{total_videos}: {safe_title}")

                        if choice == 1:
                            # Download highest quality video
                            video_stream = yt.streams.filter(only_video=True, file_extension='mp4').order_by('resolution').desc().first()
                            audio_stream = yt.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()

                            if not video_stream or not audio_stream:
                                print("No suitable streams found for this video.")
                                continue

                            # Download video and audio
                            video_path = video_stream.download(filename='video_temp.mp4', output_path='temp')
                            audio_path = audio_stream.download(filename='audio_temp.webm', output_path='temp')

                            # Merge using FFmpeg
                            output_path = os.path.join(channel_path, f"{index:02d} - {safe_title}.mp4")
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
                                output_path
                            ]

                            try:
                                subprocess.run(command, check=True, stderr=subprocess.DEVNULL)
                                # print(f"Downloaded {yt.title} in YTDL folder")
                            except subprocess.CalledProcessError as e:
                                print(f"Error occurred during merge: {e}")
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
                                print("No suitable audio stream found.")
                                continue

                            # Download WEBM audio
                            temp_path = stream.download(filename='audio_temp.webm', output_path='temp')
                            
                            if audio_choice == 1:
                                # Convert to MP3
                                output_path = os.path.join(channel_path, f"{index:02d} - {safe_title}.mp3")
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
                                    output_path
                                ]
                            else:  # audio_choice == 2
                                # Convert to WAV
                                output_path = os.path.join(channel_path, f"{index:02d} - {safe_title}.wav")
                                command = [
                                    get_ffmpeg_path(),
                                    "-hide_banner",
                                    "-loglevel", "error",
                                    "-i", temp_path,
                                    "-vn",  # No video
                                    "-acodec", "pcm_s16le",  # PCM 16-bit encoding
                                    "-ar", "44100",          # 44.1kHz sample rate
                                    "-ac", "2",              # Stereo
                                    output_path
                                ]

                            try:
                                # print(f"Converting to {os.path.splitext(output_path)[1][1:].upper()}...")
                                subprocess.run(command, check=True, stderr=subprocess.DEVNULL)
                                # print(f"Downloaded {yt.title} in YTDL folder")
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
                                        "-acodec", "libmp3lame" if audio_choice == 1 else "pcm_s16le",
                                        "-ar", "44100",
                                        "-ac", "2",
                                        output_path
                                    ]
                                    subprocess.run(alt_command, check=True, stderr=subprocess.DEVNULL)
                                    print(f"Downloaded {yt.title} in YTDL folder")
                                except subprocess.CalledProcessError as e:
                                    print(f"Error during alternative conversion: {e}")
                            finally:
                                # Clean up temporary file
                                try:
                                    os.remove(temp_path)
                                except:
                                    pass

                    except Exception as e:
                        print(f"Error processing video: {e}")
                        continue

                print("\nChannel download complete!")

            finally:
                # Clean up temp directory
                try:
                    shutil.rmtree("temp")
                except:
                    pass

            input("Press Enter to continue...")
            continue

        except ValueError:
            print("Please enter a valid number.")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"An error occurred: {e}")
            input("Press Enter to continue...") 