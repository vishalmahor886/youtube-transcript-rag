from pydantic import BaseModel

class VideoRequest(BaseModel):
    youtube_url: str

class QuestionRequest(BaseModel):
    video_id: str
    question: str

class SummaryRequest(BaseModel):
    video_id: str

class ResponseModel(BaseModel):
    response: str