from fastapi import APIRouter, HTTPException

from app.models.schemas import *
from app.services.youtube_service import extract_video_id, get_transcript
from app.utils.text_splitter import split_text
from app.services.embedding_service import get_embeddings
from app.services.vector_db_service import save_vector_store, load_vector_store
from app.services.rag_service import build_qa_chain
from app.services.summary_service import summarize_text

from fastapi.responses import StreamingResponse

from langchain_community.vectorstores import FAISS

router = APIRouter()

def normalize_url(url):
    if "shorts" in url:
        video_id = url.split("/")[-1]
        return f"https://www.youtube.com/watch?v={video_id}"
    return url


@router.post("/process-video")
def process_video(data: dict):
    try:
        youtube_url = normalize_url(data["youtube_url"])

        # extract video id safely
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[-1].split("&")[0]
        else:
            raise Exception("Invalid YouTube URL")

        print("VIDEO ID:", video_id)

        # fetch transcript
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception:
            raise Exception("Transcript not available for this video")

        return {"video_id": video_id}

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e)

@router.post("/ask")
def ask_question(request: QuestionRequest):
    embeddings = get_embeddings()

    vector_store = load_vector_store(request.video_id, embeddings)

    if not vector_store:
        raise HTTPException(status_code=404, detail="Video not processed")

    qa_chain = build_qa_chain(vector_store)
    answer = qa_chain.run(request.question)
    return {"response": answer}


@router.post("/summary")
def get_summary(request: SummaryRequest):
    video_id = request.video_id

    embeddings = get_embeddings()
    vector_store = load_vector_store(video_id, embeddings)

    if not vector_store:
        raise HTTPException(status_code=404, detail="Video not processed")

    docs = vector_store.similarity_search("summary", k=10)

    combined_text = " ".join([doc.page_content for doc in docs])

    summary = summarize_text(combined_text)

    return {"response": summary.content}