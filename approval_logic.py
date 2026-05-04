import os
import sys

from langchain_core.messages import HumanMessage

def human_approval(state):

    last_msg = state["messages"][-1].content.lower()

    if "refund" in last_msg:
        auto_approve = os.getenv("AUTO_APPROVE_REFUNDS", "").lower() in {"1", "true", "yes"}
        non_interactive = not sys.stdin.isatty()
        if auto_approve or non_interactive:
            return state

        print("\n⚠️ HIGH RISK ACTION DETECTED")
        print("Agent proposes:", last_msg)

        decision = input("Approve action? (yes / no / edit): ")

        if decision == "no":
            return {"messages": [HumanMessage(content="Refund cancelled by human")]}

        if decision == "edit":
            edited = input("Enter corrected instruction: ")
            return {"messages": [HumanMessage(content=edited)]}

    return state