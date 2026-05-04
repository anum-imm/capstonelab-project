from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from graph import app as graph_app, memory as graph_memory
from schema import ChatRequest, ChatResponse
from secured_graph import memory as secured_memory, secured_app


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_dotenv()
    _ = graph_memory
    _ = secured_memory
    yield


app = FastAPI(title="LangGraph Support API", version="1.0.0", lifespan=lifespan)


def _agent_app(use_secured: bool):
    return secured_app if use_secured else graph_app


def _run_chat_sync(agent_app: Any, state: dict[str, Any], config: dict[str, Any]) -> str:
    """Match agent_runner.run_cli: stream_mode='values'."""
    last_message = None
    for step in agent_app.stream(state, config=config, stream_mode="values"):
        last_message = step["messages"][-1]
    return last_message.content if last_message else ""


@app.get("/")
async def health_check() -> dict[str, str]:
    # Quick root check so browser hits don't return 404.
    return {"status": "ok", "message": "FastAPI is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    agent_app = _agent_app(payload.secured)
    config = {"configurable": {"thread_id": payload.thread_id}}
    state = {"messages": [HumanMessage(content=payload.message)]}

    try:
        final_answer = await asyncio.to_thread(_run_chat_sync, agent_app, state, config)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ChatResponse(
        final_answer=final_answer,
        status="success",
    )


async def sse_event_stream(payload: ChatRequest) -> AsyncGenerator[str, None]:
    agent_app = _agent_app(payload.secured)
    config = {"configurable": {"thread_id": payload.thread_id}}
    state = {"messages": [HumanMessage(content=payload.message)]}

    try:
        async for step in agent_app.astream(state, config=config, stream_mode="updates"):
            node_name = next(iter(step.keys()))
            node_payload: Any = step[node_name]

            if isinstance(node_payload, dict) and "messages" in node_payload:
                text = node_payload["messages"][-1].content
            else:
                text = str(node_payload)

            body = json.dumps({"node": node_name, "chunk": text}, ensure_ascii=True)
            yield f"data: {body}\n\n"
    except Exception as exc:
        err = json.dumps({"error": str(exc)}, ensure_ascii=True)
        yield f"data: {err}\n\n"


@app.post("/stream")
async def stream_chat(payload: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        sse_event_stream(payload),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
