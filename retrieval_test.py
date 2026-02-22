from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def search_knowledge(query, filter_dict=None):
    vector_db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=OpenAIEmbeddings(),
        collection_name="ecommerce_kb"
    )

    # Perform search with optional metadata filtering (Mandatory Task 2)
    results = vector_db.similarity_search(query, k=1, filter=filter_dict)
    
    if results:
        print(f"\nQuery: {query}")
        print(f"Result: {results[0].page_content}")
        print(f"Metadata: {results[0].metadata}")
    else:
        print("No results found.")

if __name__ == "__main__":
    # Test 1: General Query
    search_knowledge("What is the return window for electronics?")

    # Test 2: Metadata Filtered Query
    # This only looks for docs where department is 'customer_service'
    search_knowledge("Shipping fees for members", filter_dict={"department": "customer_service"})