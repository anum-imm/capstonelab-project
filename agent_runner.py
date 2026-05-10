from __future__ import annotations

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage


def run_cli(agent_app, thread_id: str, banner: str) -> None:
    """
    Shared interactive runner for LangGraph apps.
    """
    load_dotenv()
    config = {"configurable": {"thread_id": thread_id}}

    print(f"{banner}\n")

    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break

        state = {"messages": [HumanMessage(content=user_input)]}
        last_msg = None

        for step in agent_app.stream(state, config=config, stream_mode="values"):
            last_msg = step["messages"][-1]

        if last_msg:
            print("\nAgent:", last_msg.content)
            
            feedback = input("\nFeedback (good/bad): ").strip().lower()
            if feedback not in ["good", "bad"]:
                feedback = "neutral"
                
            # Log interaction
            try:
                import json
                import os
                log_file = "feedback_log.json"
                logs = []
                if os.path.exists(log_file):
                    with open(log_file, "r") as f:
                        try:
                            logs = json.load(f)
                        except json.JSONDecodeError:
                            pass
                logs.append({
                    "user_input": user_input,
                    "agent_response": last_msg.content,
                    "feedback": feedback
                })
                with open(log_file, "w") as f:
                    json.dump(logs, f, indent=4)
            except Exception as e:
                print(f"Failed to log feedback: {e}")
