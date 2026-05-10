import os
from typing import List
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
load_dotenv(os.path.join(parent_dir, ".env"))

index_path = os.path.join(base_dir, "faiss_index")
if os.path.exists(index_path):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
else:
    retriever = None

class RetrieveInput(BaseModel):
    query: str = Field(..., description="The user query to search the vectorstore for.")

@tool(args_schema=RetrieveInput)
def retrieve_tool(query: str) -> List[str]:
    """Search the vector database for relevant university documents."""
    if retriever:
        docs = retriever.invoke(query)
        return [doc.page_content for doc in docs]
    return []

class WebSearchInput(BaseModel):
    query: str = Field(..., description="The user query to search the web for.")

@tool(args_schema=WebSearchInput)
def web_search_tool(query: str) -> str:
    """Fallback search tool to search the internet when internal documents are insufficient."""
    search = DuckDuckGoSearchRun()
    return search.invoke(query)
