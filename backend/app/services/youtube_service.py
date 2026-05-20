from youtube_transcript_api import YouTubeTranscriptApi 
import re
import os


## Extract video id
def extract_video_id(url: str)-> str:

    patterns = [
        r"(?:v=)([0-9A-Za-z_-]{11})",          # https://www.youtube.com/watch?v=...
        r"(?:youtu\.be/)([0-9A-Za-z_-]{11})",  # https://youtu.be/...
        r"(?:embed/)([0-9A-Za-z_-]{11})",      # https://youtube.com/embed/...
        r"(?:shorts/)([0-9A-Za-z_-]{11})",     # https://youtube.com/shorts/...
    ]

    #pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    #match = re.search(pattern, url)
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Invalid Youtube URL")



def get_transcript(video_id: str) -> str:
    try:
        # 1. Determine the path to your cookies.txt file
        # Check the Render secret file location first, fallback to local for development
        cookies_path = "/opt/render/project/src/cookies.txt"
        if not os.path.exists(cookies_path):
            cookies_path = "cookies.txt"

        youtube_transcript = YouTubeTranscriptApi()

        # 2. Fetch the transcript list using cookies if the file exists
        if os.path.exists(cookies_path):
            transcript_list = youtube_transcript.list(video_id, cookies=cookies_path)
        else:
            # Fallback for local testing if you haven't set up a local cookies.txt yet
            transcript_list = youtube_transcript.list(video_id)

        # 3. Your original fallback logic (Try English, fallback to Hindi)
        try:
            transcript = transcript_list.find_transcript(["en"])
        except Exception:
            transcript = transcript_list.find_transcript(["hi"])
        
        # 4. Fetch the raw pieces and merge them into a single string
        data = transcript.fetch()
        
        # Note: 'element' is a dictionary, so we access it using ['text'] instead of .text
        text = " ".join(element['text'] for element in data)
        return text
    
    except Exception as e:
        raise Exception(f"Transcript error: {str(e)}")
