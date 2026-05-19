from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
import os
from dotenv import load_dotenv
load_dotenv("backend/.env")
def summarize_text(text:str):
        
    base_llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
        temperature=0,
        huggingfacehub_api_token=os.getenv("ACCESS_TOKEN_HUGGINGFACE")
    )

    llm = ChatHuggingFace(llm=base_llm)

    prompt = PromptTemplate(
        template="""
Summarize the following Youtube Transcript:\n\n{text}
""",
        input_variables=["text"]
    )

    return llm.invoke(prompt.format(text=text))
