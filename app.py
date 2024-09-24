import streamlit as st
from dotenv import load_dotenv
import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

# Configure Google API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt for summarization
prompt = """
You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing important points in 250 words.
Please provide the summary of the text given here:
"""

# Function to extract video ID from YouTube URL
def get_video_id(youtube_url):
    """
    Extract the video ID from various possible YouTube URL formats.
    """
    # Regex pattern for YouTube URL
    video_id_patterns = [
        r"^https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",  # Match YouTube watch URLs
        r"^https?://youtu\.be/([a-zA-Z0-9_-]{11})",  # Match short YouTube URLs
    ]
    
    for pattern in video_id_patterns:
        match = re.match(pattern, youtube_url)
        if match:
            return match.group(1)  # Return the video ID
    
    return None  # Return None if no match is found

# Function to extract transcript using YouTubeTranscriptApi
def extract_transcript_details(youtube_video_url):
    try:
        video_id = get_video_id(youtube_video_url)
        
        if video_id is None:
            raise ValueError("Invalid YouTube URL. Please enter a valid YouTube video URL.")
        
        # Get the transcript using the video ID
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine the transcript text
        transcript = " ".join([item["text"] for item in transcript_text])

        return transcript

    except Exception as e:
        raise e

# Function to generate content from the Gemini model
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit app interface
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

# Show video thumbnail if link is provided
if youtube_link:
    video_id = get_video_id(youtube_link)
    
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

# Button to get detailed notes
if st.button("Get Detailed Notes"):
    try:
        transcript_text = extract_transcript_details(youtube_link)

        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)
        else:
            st.error("Could not retrieve transcript. Please check the video or try another.")
    except Exception as e:
        st.error(f"Error: {e}")
