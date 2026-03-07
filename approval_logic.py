from langchain_core.messages import HumanMessage

def human_approval(state):

    last_msg = state["messages"][-1].content.lower()

    if "refund" in last_msg:

        print("\n⚠️ HIGH RISK ACTION DETECTED")
        print("Agent proposes:", last_msg)

        decision = input("Approve action? (yes / no / edit): ")

        if decision == "no":
            return {"messages": [HumanMessage(content="Refund cancelled by human")]}

        if decision == "edit":
            edited = input("Enter corrected instruction: ")
            return {"messages": [HumanMessage(content=edited)]}

    return state