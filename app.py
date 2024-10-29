import streamlit as st
import yt_dlp
import tempfile
import os

# タイトルと説明
st.title("YouTube Video Downloader")
st.write("Enter the URL of a YouTube video, and download the video file.")

# YouTubeのURL入力
url = st.text_input("YouTube Video URL", "")

# URLが入力されている場合
if url:
    try:
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # yt-dlp設定
        def progress_hook(d):
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes', 0)
                downloaded_bytes = d.get('downloaded_bytes', 0)
                if total_bytes > 0:
                    progress = downloaded_bytes / total_bytes
                    progress_bar.progress(progress)
                    status_text.text(f"Downloading: {progress * 100:.2f}%")

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # 最高の品質でダウンロード
            'outtmpl': '%(title)s.%(ext)s',  # ファイル名のテンプレート
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],  # Add the progress hook
        }

        # ダウンロードボタンが押されたとき
        if st.button("Download Video"):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 動画情報を取得
                info_dict = ydl.extract_info(url, download=False)
                video_title = info_dict.get('title', 'video')
                video_ext = info_dict.get('ext', 'mp4')

                # 一時ディレクトリに動画をダウンロード
                with tempfile.TemporaryDirectory() as tmpdir:
                    ydl_opts['outtmpl'] = os.path.join(tmpdir, f"{video_title}.%(ext)s")
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])

                    # ダウンロードしたファイルのパスを取得
                    video_path = os.path.join(tmpdir, f"{video_title}.{video_ext}")

                    # 動画をバイナリデータとして読み込む
                    with open(video_path, "rb") as file:
                        video_bytes = file.read()

                    # ダウンロードリンクを提供
                    st.download_button(label="Click to download the video",
                                       data=video_bytes,
                                       file_name=f"{video_title}.{video_ext}",
                                       mime="video/mp4")
    except Exception as e:
        st.error(f"An error occurred: {e}")