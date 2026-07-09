from fastapi import APIRouter
from app.schemas.chat import ChatRequest
from app.services.qdrant_service import QdrantService
from app.services.llm_service import LLMService

router = APIRouter(
    prefix="/v1",
    tags=["Chat"]
)
@router.get("/models")
def models():
    return {
        "object": "list",
        "data": [
            {
                "id": "llama3.2:3b",
                "object": "model",
                "owned_by": "local"
            }
        ]
    }


@router.post("/chat/completions")
def chat(request: ChatRequest):

    question = request.messages[-1].content

    qdrant = QdrantService()

    results = qdrant.search(question)

    chunks = []

    for result in results:
        chunks.append(result.payload["text"])

    llm = LLMService()

    answer = llm.generate(question, chunks)

    return {
        "id": "chatcmpl-1",
        "object": "chat.completion",

        "choices": [
            {
                "index": 0,

                "message": {
                    "role": "assistant",
                    "content": answer
                },

                "finish_reason": "stop"
            }
        ]
    }