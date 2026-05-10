from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from approval_logic import human_approval
from tools import search_policies, get_order_details, check_shipping_status, approve_refund


# -------------------------
# MEMORY
# -------------------------
memory = MemorySaver()


# -------------------------
# STATE
# -------------------------
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# -------------------------
# LLMs
# -------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
supervisor_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# -------------------------
# POLICY AGENT
# -------------------------
policy_agent = create_react_agent(
    llm,
    tools=[search_policies, approve_refund],
    prompt=SystemMessage(
        content="""
You are a customer support policy specialist.

You can:
- answer policy questions
- approve refunds when policy allows

Refunds are high-risk actions and require human approval.

Always check policy before approving refund.
"""
    ),
    checkpointer=memory,
)


# -------------------------
# ORDER AGENT
# -------------------------
order_agent = create_react_agent(
    llm,
    tools=[get_order_details, check_shipping_status],
    prompt=SystemMessage(
        content="""
You are an order management assistant.

You must retrieve order information using tools.

Rules:
- Use get_order_details for order queries.
- Use check_shipping_status for delivery queries.
- Never guess order information.
- If the user does not provide an order ID, politely ask them for it before proceeding.
"""
    ),
    checkpointer=memory,
)


# -------------------------
# SUPERVISOR NODE
# -------------------------
def supervisor(state: AgentState):
    return state


# -------------------------
# ROUTER
# -------------------------
def supervisor_router(state: AgentState):

    question = state["messages"][-1].content

    prompt = f"""
You are a supervisor managing two agents:

1. policy_agent → handles refund, return, and policy questions
2. order_agent → handles order details, shipping, and delivery questions

Respond with ONLY one word:
policy_agent
order_agent

User question:
{question}
"""

    response = supervisor_llm.invoke(prompt).content.strip().lower()

    if "order_agent" in response:
        return "order_agent"

    return "policy_agent"


# -------------------------
# GRAPH
# -------------------------
workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor)
workflow.add_node("policy_agent", policy_agent)
workflow.add_node("order_agent", order_agent)
workflow.add_node("human_check", human_approval)

workflow.set_entry_point("supervisor")

workflow.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {
        "policy_agent": "policy_agent",
        "order_agent": "order_agent",
    },
)

# Order questions end directly
workflow.add_edge("order_agent", END)

# Policy agent goes through HITL
workflow.add_edge("policy_agent", "human_check")
workflow.add_edge("human_check", END)


# -------------------------
# COMPILE
# -------------------------
app = workflow.compile(checkpointer=memory)