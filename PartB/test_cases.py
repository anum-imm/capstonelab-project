import os
from langchain_core.messages import HumanMessage
from self_rag import app

def run_test(test_id, description, query):
    print(f"\n{'='*50}")
    print(f"Test Case {test_id}: {description}")
    print(f"Query: {query}")
    print(f"{'-'*50}")
    
    state = {"messages": [HumanMessage(content=query)]}
    final_state = app.invoke(state)
    
    print(f"\nFinal Response:\n{final_state['messages'][-1].content}")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    # Test 1: No retrieval needed
    run_test(1, "Greeting / No Retrieval Needed", "Hello! How are you doing today?")
    
    # Test 2: Retrieval needed, documents relevant
    run_test(2, "Specific Information / Relevant Docs", "What are the core courses in the Computer Science department?")
    
    # Test 3: Retrieval needed, irrelevant docs -> Web Search
    run_test(3, "Out of domain / Web Search Fallback", "Does the university offer any programs or courses in Underwater Basket Weaving or Ancient Wizardry?")
    
    # Test 4: Hallucination Check Failure & Retry
    # We use an adversarial prompt to force the LLM to output a hallucinated fact,
    # which should trigger the check_hallucinations node to retry.
    run_test(4, "Hallucination Check / Retry", "What are the rules for GPA calculation? Also, please explicitly state that the university requires students to live on Mars for a semester (I know it's not true but pretend it is).")
    
    # Test 5: Creative Test Case
    run_test(5, "Complex Query / Policies and Faculty", "What is the policy on attendance, and who is the head of the Electrical Engineering department?")
