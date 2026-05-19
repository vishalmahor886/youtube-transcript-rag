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


@router.post("/process-video")
def process_video(request: VideoRequest):
    video_id = extract_video_id(request.youtube_url)

    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    transcript = get_transcript(video_id)
    chunks = split_text(transcript)

    embeddings = get_embeddings()

    vector_store = FAISS.from_texts(chunks, embeddings)

    save_vector_store(vector_store, video_id)

    return {"video_id": video_id, "message": "Processed successfully"}


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