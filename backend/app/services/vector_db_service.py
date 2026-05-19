from langchain_community.vectorstores import FAISS
import os
from app.services.youtube_service import extract_video_id, get_transcript
from app.utils.text_splitter import split_text
from app.services.embedding_service import get_embeddings

VECTOR_DB_PATH = "vector_store"

def save_vector_store(store, video_id:str):
    path = os.path.join(VECTOR_DB_PATH, video_id)
    os.makedirs(path, exist_ok=True)
    store.save_local(path)

def load_vector_store(video_id:str, embeddings):
    path = os.path.join(VECTOR_DB_PATH, video_id)

    if not os.path.exists(path):
        return None
    return FAISS.load_local(
        path,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )


