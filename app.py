import streamlit as st
import yt_dlp
import tempfile
import os
from typing import Optional, Dict, Any
import re

def validate_youtube_url(url: str) -> bool:
    """Validate if the provided URL is a valid YouTube URL."""
    youtube_regex = (
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return bool(re.match(youtube_regex, url))

def format_size(bytes: int) -> str:
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} TB"

def get_video_info(url: str) -> Optional[Dict[str, Any]]:
    """Fetch video information without downloading."""
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as e:
        st.error(f"Error fetching video info: {str(e)}")
        return None

def download_video(url: str, quality: str, progress_bar, status_text) -> Optional[tuple]:
    """Download video with specified quality and return video data and metadata."""
    def progress_hook(d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                progress = downloaded_bytes / total_bytes
                progress_bar.progress(progress)
                status_text.text(
                    f"Downloading: {progress * 100:.1f}% "
                    f"({format_size(downloaded_bytes)} / {format_size(total_bytes)})"
                )

    try:
        format_selection = {
            'High': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'Medium': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
            'Low': 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst'
        }

        ydl_opts = {
            'format': format_selection.get(quality, 'best'),
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts['outtmpl'] = os.path.join(tmpdir, '%(title)s.%(ext)s')
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Download video
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'video').replace('/', '_')
                filename = f"{video_title}.mp4"
                video_path = os.path.join(tmpdir, filename)
                with open(video_path, "rb") as f:
                    return f.read(), filename, info
        return None, None, None
    except Exception as e:
        st.error(f"Download failed: {str(e)}")
        return None, None, None

def download_audio(url: str, progress_bar, status_text) -> Optional[tuple]:
    """Download audio and return audio data and metadata."""
    def progress_hook(d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                progress = downloaded_bytes / total_bytes
                progress_bar.progress(progress)
                status_text.text(
                    f"Downloading: {progress * 100:.1f}% "
                    f"({format_size(downloaded_bytes)} / {format_size(total_bytes)})"
                )

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts['outtmpl'] = os.path.join(tmpdir, '%(title)s.%(ext)s')
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Download audio
                info = ydl.extract_info(url, download=True)
                audio_title = info.get('title', 'audio').replace('/', '_')
                filename = f"{audio_title}.mp3"
                audio_path = os.path.join(tmpdir, filename)
                with open(audio_path, "rb") as f:
                    return f.read(), filename, info
        return None, None, None
    except Exception as e:
        st.error(f"Download failed: {str(e)}")
        return None, None, None

def input_url_and_get_info():
    """Handle URL input, validation, and fetching video info."""
    url = st.text_input("Enter YouTube URL", help="Paste the URL of the YouTube video you want to download")
    if url:
        if not validate_youtube_url(url):
            st.error("Please enter a valid YouTube URL")
            return None, None
        else:
            # Fetch video info
            info = get_video_info(url)
            if info:
                return url, info
    return None, None

def display_video_details(info):
    """Display video details."""
    st.markdown("### Video Details")
    st.image(info.get('thumbnail'), use_column_width=True)  # Display thumbnail image
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Title:** {info.get('title', 'Unknown')}")
        duration_seconds = info.get('duration', 0)
        st.markdown(f"**Duration:** {int(duration_seconds // 60)}:{int(duration_seconds % 60):02d}")
    with col2:
        st.markdown(f"**Channel:** {info.get('channel', 'Unknown')}")
        st.markdown(f"**Views:** {info.get('view_count', 0):,}")

# Set page config
st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎥",
    layout="centered"
)

# Add custom CSS
st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
            font-size: 20px;
            margin-top: 20px;
        }
        .download-info {
            padding: 10px;
            background-color: #f0f2f6;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Main app interface
st.title("🎥 YouTube Downloader")
st.write("Download YouTube videos or audio in your preferred format.")

# URL input and video info fetching
url, info = input_url_and_get_info()

if info:
    display_video_details(info)
    
    # User selects whether to download video or audio
    download_type = st.radio("Select Download Type", ["Video", "Audio"])
    
    if download_type == "Video":
        # Quality selection
        quality = st.select_slider(
            "Select Quality",
            options=['Low', 'Medium', 'High'],
            value='High'
        )
        if st.button("Download Video"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            video_data, filename, video_info = download_video(
                url, quality, progress_bar, status_text
            )
            if video_data and filename:
                status_text.text("Download complete! Click below to save the video.")
                progress_bar.progress(1.0)
                st.download_button(
                    label="Save Video",
                    data=video_data,
                    file_name=filename,
                    mime="video/mp4"
                )
                st.success("Video successfully processed! Click the button above to save it.")
    else:
        if st.button("Download Audio"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            audio_data, filename, audio_info = download_audio(
                url, progress_bar, status_text
            )
            if audio_data and filename:
                status_text.text("Download complete! Click below to save the audio.")
                progress_bar.progress(1.0)
                st.download_button(
                    label="Save Audio",
                    data=audio_data,
                    file_name=filename,
                    mime="audio/mp3"
                )
                st.success("Audio successfully processed! Click the button above to save it.")