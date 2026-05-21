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
        # 1. Cookies path (Render + local fallback)
        cookies_path = "/opt/render/project/src/cookies.txt"
        if not os.path.exists(cookies_path):
            cookies_path = "cookies.txt"

        youtube_transcript = YouTubeTranscriptApi()

        # 2. Load transcript list (with cookies if available)
        if os.path.exists(cookies_path):
            transcript_list = youtube_transcript.list(video_id, cookies=cookies_path)
        else:
            transcript_list = youtube_transcript.list(video_id)

        # 3. Language fallback (EN → HI)
        try:
            transcript = transcript_list.find_transcript(["en"])
        except Exception:
            transcript = transcript_list.find_transcript(["hi"])

        # 4. Fetch transcript
        data = transcript.fetch()

        # ✅ FIX: handle object properly
        text = " ".join(
            element.text if hasattr(element, "text") else element["text"]
            for element in data
        )

        return text

    except Exception as e:
        print("❌ Transcript error:", e)
        return None