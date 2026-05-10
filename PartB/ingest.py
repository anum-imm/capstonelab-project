import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

def ingest_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = [
        "CS_Department_Catalog.pdf",
        "EE_Department_Catalog.pdf",
        "BBA_Department_Catalog.pdf",
        "University_Academic_Policies.pdf",
        "Faculty_Directory.pdf"
    ]
    
    docs = []
    for file in files:
        filepath = os.path.join(base_dir, file)
        if os.path.exists(filepath):
            print(f"Loading {file}...")
            loader = PyPDFLoader(filepath)
            loaded_docs = loader.load()
            
            # Add metadata about department/document type based on filename
            doc_type = "catalog" if "Catalog" in file else ("policy" if "Policies" in file else "directory")
            department = file.split("_")[0] if doc_type == "catalog" else "general"
            
            for doc in loaded_docs:
                doc.metadata["source_file"] = file
                doc.metadata["doc_type"] = doc_type
                doc.metadata["department"] = department
            
            docs.extend(loaded_docs)
        else:
            print(f"Warning: {file} not found.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunks = text_splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks.")
    
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    index_path = os.path.join(base_dir, "faiss_index")
    vectorstore.save_local(index_path)
    print("FAISS index saved successfully.")

if __name__ == "__main__":
    ingest_data()
