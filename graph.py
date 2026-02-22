from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages # Required for correct message history
from dotenv import load_dotenv
import os

from tools import search_policies, get_order_details, check_shipping_status

load_dotenv()

# 1️⃣ DEFINE STATE WITH REDUCER
class AgentState(TypedDict):
    # Annotated with add_messages ensures new messages are appended 
    # to history instead of overwriting, preventing OpenAI API errors.
    messages: Annotated[Sequence[BaseMessage], add_messages]

# 2️⃣ LOAD LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
tools = [search_policies, get_order_details, check_shipping_status]
llm_with_tools = llm.bind_tools(tools)

# 3️⃣ AGENT NODE
def agent_node(state: AgentState):
    # Just return the new response; 'add_messages' handles the merge
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 4️⃣ TOOL NODE
tool_node = ToolNode(tools)

# 5️⃣ ROUTER FUNCTION
def router(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"

# 6️⃣ BUILD GRAPH
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    router,
    {
        "tools": "tools",
        "end": END,
    },
)

workflow.add_edge("tools", "agent")

app = workflow.compile()

import os
from graph import app

# 1. Get the graph object
graph = app.get_graph()

# 2. To get a PNG with details, we use the mermaid draw method
try:
    # This requires 'pygraphviz' or 'graphviz' system-level installs
    # It generates a PNG file of the current workflow
    graph_png = graph.draw_mermaid_png()
    
    with open("detailed_graph.png", "wb") as f:
        f.write(graph_png)
    print("Success! 'detailed_graph.png' has been saved to your project folder.")

except Exception as e:
    print(f"PNG generation failed: {e}")
    # Fallback: Print the Mermaid text code
    print("\nCopy the text below into https://mermaid.live to see a detailed version:")
    print(graph.draw_mermaid())