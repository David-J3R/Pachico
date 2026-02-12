import asyncio

from fastapi import APIRouter
from pydantic import BaseModel

from App.service import invoke_agent

router = APIRouter(prefix="/api")


class ChatRequest(BaseModel):
    message: str
    thread_id: str


class ChatResponse(BaseModel):
    text: str
    file_paths: list[str]


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = await asyncio.to_thread(invoke_agent, request.message, request.thread_id)
    return ChatResponse(text=response.text, file_paths=response.file_paths)
