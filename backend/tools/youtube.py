import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

def _execute_youtube_search(youtube, query, max_results, **kwargs):
    """Helper function to execute a YouTube search and format results."""
    try:
        search_response = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=max_results,
            type='video',
            **kwargs
        ).execute()

        if not search_response.get('items'):
            return None

        results = []
        for item in search_response['items']:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            results.append(f"- {title}: {video_url}")
        
        return "\n".join(results)

    except HttpError:
        return None

def find_youtube_video(destination: str) -> str:
    """
    Finds relevant travel vlogs and shorts for a destination using the YouTube Data API.
    """
    if not API_KEY:
        return "Error: Google API key is not configured in the .env file."

    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        
        vlog_query = f"{destination} travel vlog"
        vlog_results = _execute_youtube_search(youtube, vlog_query, 3)
        
        shorts_query = f"{destination} travel shorts"
        shorts_results = _execute_youtube_search(youtube, shorts_query, 3, videoDuration='short')
        
        output = ""
        if vlog_results:
            output += f"Here are some popular travel vlogs for {destination}:\n{vlog_results}\n\n"
        
        if shorts_results:
            output += f"Here are some trending travel shorts for {destination}:\n{shorts_results}\n"

        if not output:
            return f"Sorry, I couldn't find any travel videos for {destination}."

        return output.strip()

    except Exception as e:
        return f"An unexpected error occurred: {e}"