import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Set your API Key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

def run_ingestion():
    # 1. Load the knowledge source
    loader = TextLoader("data/refund_policy.txt")
    documents = loader.load()

    # 2. Semantic Chunking
    # We use a small chunk size to ensure specific policies are isolated
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    # 3. Metadata Enrichment (Mandatory Task 1)
    for chunk in chunks:
        chunk.metadata["doc_type"] = "policy"
        chunk.metadata["department"] = "customer_service"
        chunk.metadata["last_updated"] = "2024-Q1"

    # 4. Vector Indexing (Mandatory Task 3)
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(),
        persist_directory="./chroma_db",
        collection_name="ecommerce_kb"
    )
    
    print(f"Successfully indexed {len(chunks)} chunks to ChromaDB.")

if __name__ == "__main__":
    run_ingestion()