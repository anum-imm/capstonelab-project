import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# --- DYNAMIC PATH SETUP ---
# Gets the absolute path to the directory where tools.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Corrected filenames based on your VS Code explorer screenshot
REFUND_FILE = os.path.join(DATA_DIR, "refund_policy.txt") # Changed to singular
DB_FILE = os.path.join(DATA_DIR, "orders.db")
SHIPPING_FILE = os.path.join(DATA_DIR, "shipping_log.csv")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index")

# --- VECTOR DB TOOL ---
class PolicySearchInput(BaseModel):
    query: str = Field(..., description="User question related to refund or shipping policies.")

def get_vector_db():
    embeddings = OpenAIEmbeddings()
    if os.path.exists(FAISS_INDEX_PATH):
        # allow_dangerous_deserialization is required for loading local pickle files
        return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    
    if not os.path.exists(REFUND_FILE):
        raise FileNotFoundError(f"Missing policy file at: {REFUND_FILE}")
        
    with open(REFUND_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    db = FAISS.from_texts(lines, embeddings)
    db.save_local(FAISS_INDEX_PATH)
    return db

vectordb = get_vector_db()

@tool(args_schema=PolicySearchInput)
def search_policies(query: str) -> str:
    """Search business policies for refund and shipping rules."""
    try:
        docs = vectordb.similarity_search(query, k=3)
        return "\n".join([doc.page_content for doc in docs])
    except Exception as e:
        return f"Error searching policies: {e}"

# --- ORDER DATABASE TOOL ---
class OrderLookupInput(BaseModel):
    order_id: int = Field(..., description="The order ID to retrieve details for.")

@tool(args_schema=OrderLookupInput)
def get_order_details(order_id: int) -> str:
    """Retrieve internal order data from the SQL database."""
    try:
        # Convert numeric ID to the string format in your DB (e.g., 101 -> ORD-1001)
        # Based on your image, it looks like the format is ORD-100X
        formatted_id = f"ORD-{order_id}" 
        
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            # Changed 'order_id' to 'id' to match your screenshot
            cursor.execute("SELECT * FROM orders WHERE id = ?", (formatted_id,))
            result = cursor.fetchone()
            return f"Order Details: {result}" if result else f"Order {formatted_id} not found."
    except Exception as e:
        return f"Database error: {e}"

# --- SHIPPING TOOL ---
@tool(args_schema=OrderLookupInput) # Reusing schema since it's just an order_id
def check_shipping_status(order_id: int) -> str:
    """Check the CSV shipping log for delivery status."""
    try:
        df = pd.read_csv(SHIPPING_FILE)
        record = df[df["order_id"] == order_id]
        return record.to_string(index=False) if not record.empty else "No shipping record."
    except Exception as e:
        return f"Shipping log error: {e}"