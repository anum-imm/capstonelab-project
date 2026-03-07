from graph import app
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

config = {"configurable": {"thread_id": "session_1"}}

print("AI Support Agent Started\n")

while True:

    user_input = input("User: ")

    if user_input.lower() == "exit":
        break

    state = {
        "messages": [HumanMessage(content=user_input)]
    }

    last_msg = None

    for step in app.stream(state, config=config, stream_mode="values"):
        last_msg = step["messages"][-1]

    if last_msg:
        print("\nAgent:", last_msg.content)