from langchain_classic.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
import os


def build_qa_chain(vector_store):
    # ✅ Retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    # ✅ LLM (use a valid HF model)
    base_llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
        temperature=0,
        huggingfacehub_api_token=os.getenv("ACCESS_TOKEN_HUGGINGFACE")
    )

    llm = ChatHuggingFace(llm=base_llm)

    # ✅ QA Chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False
    )

    return qa_chain
