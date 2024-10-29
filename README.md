# YouTube Video Downloader

This is a simple web application that allows you to download YouTube videos by entering their URL. The application is built using Streamlit and yt-dlp.

## Features

- **Enter YouTube URL**: Input the URL of the YouTube video you wish to download.
- **Download Video**: Provides a button to download the video in the highest available resolution.

## How to Run

1. **Install Dependencies**: Make sure you have Python installed, then install the required packages using pip:

   ```bash
   pip install streamlit yt-dlp
   ```

2. **Run the Application**: Use Streamlit to run the app:

   ```bash
   streamlit run app.py
   ```

3. **Access the App**: Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`).

## Error Handling

- **Invalid URL**: If the URL is not a valid YouTube URL, an error message will be displayed.
- **General Errors**: Any other errors will be caught and displayed to the user.

## Note

- Ensure you have a stable internet connection to download videos.
- The downloaded video will be saved with the video's title as the filename in the current directory.

## License

This project is licensed under the MIT License.
