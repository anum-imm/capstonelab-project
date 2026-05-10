from langchain_core.messages import HumanMessage
from graph import app

def run_interactive():
    print("Welcome to the University Course Advisory Agent!")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        user_input = input("User: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
            
        state = {"messages": [HumanMessage(content=user_input)]}
        final_state = app.invoke(state)
        
        print(f"\nAgent: {final_state['messages'][-1].content}\n")

if __name__ == "__main__":
    run_interactive()
