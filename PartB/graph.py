import os
from typing import TypedDict, Annotated, Sequence, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from tools import retrieve_tool, web_search_tool

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    context: List[str]
    retries: int

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    binary_score: str = Field(description="Documents are relevant to the question, 'yes' or 'no'")

class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""
    binary_score: str = Field(description="Answer is grounded in the facts, 'yes' or 'no'")

def retrieve(state: AgentState):
    print("---RETRIEVE---")
    question = state["messages"][-1].content
    context = retrieve_tool.invoke({"query": question})
    return {"context": context}

def grade_documents(state: AgentState):
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["messages"][-1].content
    docs = state.get("context", [])
    
    structured_llm_grader = llm.with_structured_output(GradeDocuments)
    system = """You are a grader assessing relevance of a retrieved document to a user question.
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant.
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
    
    filtered_docs = []
    for doc in docs:
        score = structured_llm_grader.invoke([SystemMessage(content=system)] + [HumanMessage(content=f"Retrieved document: \n\n {doc} \n\n User question: {question}")])
        if score.binary_score == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(doc)
        else:
            print("---GRADE: DOCUMENT IRRELEVANT---")
            
    return {"context": filtered_docs}

def web_search(state: AgentState):
    print("---WEB SEARCH---")
    question = state["messages"][-1].content
    docs = web_search_tool.invoke({"query": question})
    return {"context": [docs]}

def generate(state: AgentState):
    print("---GENERATE---")
    question = state["messages"][-1].content
    context = state.get("context", [])
    context_str = "\n\n".join(context) if context else "No specific university context available. Provide a general response or say you don't know."
    
    system = """You are a helpful university assistant. 
    Use the following pieces of retrieved context to answer the question if applicable.
    If you don't know the answer or the context doesn't have it, just say that you don't know.
    Context: {context}"""
    
    msg = llm.invoke([SystemMessage(content=system.format(context=context_str))] + [HumanMessage(content=question)])
    return {"messages": [msg]}

def route_question(state: AgentState):
    print("---ROUTE QUESTION---")
    question = state["messages"][-1].content
    system = """You are an expert at routing a user question to a vectorstore or answering directly.
    The vectorstore contains documents related to university courses, prerequisites, faculty, policies, grading, fees, etc.
    If the question is a greeting (e.g. "hi", "hello"), or general knowledge (e.g. "What does GPA stand for?"), output 'direct_answer'.
    If the question is about specific university information, output 'vectorstore'.
    Respond ONLY with 'direct_answer' or 'vectorstore'."""
    response = llm.invoke([SystemMessage(content=system)] + [HumanMessage(content=question)]).content.strip().lower()
    
    if "direct_answer" in response:
        print("---ROUTE QUESTION TO DIRECT ANSWER---")
        return "generate"
    print("---ROUTE QUESTION TO RAG---")
    return "retrieve"

def decide_to_generate(state: AgentState):
    print("---ASSESS GRADED DOCUMENTS---")
    filtered_docs = state.get("context", [])
    if not filtered_docs:
        print("---DECISION: ALL DOCUMENTS IRRELEVANT, ROUTE TO WEB SEARCH---")
        return "web_search"
    print("---DECISION: GENERATE---")
    return "generate"

def check_hallucinations(state: AgentState):
    print("---CHECK HALLUCINATIONS---")
    if not state.get("context"):
        print("---NO CONTEXT (DIRECT ANSWER), SKIP HALLUCINATION CHECK---")
        return "useful"

    question = state["messages"][0].content
    generation = state["messages"][-1].content
    context = state.get("context", [])
    retries = state.get("retries", 0)
    
    if retries >= 2:
        print("---MAX RETRIES REACHED---")
        return "max_retries"
        
    context_str = "\n\n".join(context)
    
    structured_llm_grader = llm.with_structured_output(GradeHallucinations)
    system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts.
    Give a binary score 'yes' or 'no'. 'yes' means that the answer is completely grounded in / supported by the set of facts."""
    
    score = structured_llm_grader.invoke([SystemMessage(content=system)] + [HumanMessage(content=f"Set of facts: \n\n {context_str} \n\n LLM generation: {generation}")])
    
    if score.binary_score == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        return "useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RETRY---")
        return "not_supported"

def max_retries_node(state: AgentState):
    msg = AIMessage(content="I'm sorry, I could not verify the information from our authoritative sources to answer your query securely. Please try asking in a different way.")
    return {"messages": [msg]}

def increment_retry(state: AgentState):
    return {"retries": state.get("retries", 0) + 1}

workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("web_search", web_search)
workflow.add_node("generate", generate)
workflow.add_node("max_retries_node", max_retries_node)
workflow.add_node("increment_retry", increment_retry)

workflow.add_conditional_edges(
    START,
    route_question,
    {
        "retrieve": "retrieve",
        "generate": "generate",
    },
)

workflow.add_edge("retrieve", "grade_documents")

workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "web_search": "web_search",
        "generate": "generate",
    },
)

workflow.add_edge("web_search", "generate")

workflow.add_conditional_edges(
    "generate",
    check_hallucinations,
    {
        "not_supported": "increment_retry",
        "useful": END,
        "max_retries": "max_retries_node",
    },
)

workflow.add_edge("increment_retry", "generate")
workflow.add_edge("max_retries_node", END)

app = workflow.compile()
