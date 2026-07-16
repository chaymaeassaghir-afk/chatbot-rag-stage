from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest
from app.services.qdrant_service import QdrantService
from app.services.llm_service import LLMService
from app.services.chunk_service import ChunkService
from app.services.reranker_service import RerankerService
from app.dependencies.auth import require_user, require_admin

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
    chunk_service = ChunkService()

    # Recherche sémantique
    semantic_results = qdrant.search(question, limit=5)

    # Recherche full-text
    keyword_results = chunk_service.search(question, limit=5)

    final_results = []
    seen = set()

    # Ajouter les résultats Qdrant
    for r in semantic_results:

        key = (r.payload["document_id"], r.payload["chunk_id"])

        if key not in seen:

            seen.add(key)

            final_results.append({
                "document_id": r.payload["document_id"],
                "document": r.payload["document_name"],
                "chunk_id": r.payload["chunk_id"],
                "text": r.payload["text"],
                "score": r.score,
                "source": "semantic"
            })

    # Ajouter les résultats PostgreSQL
    for r in keyword_results:

        key = (r.document_id, r.chunk_id)

        if key not in seen:

            seen.add(key)

            final_results.append({
                "document_id": r.document_id,
                "document": None,
                "chunk_id": r.chunk_id,
                "text": r.text,
                "score": None,
                "source": "keyword"
            })

    # Reranking
    reranker = RerankerService()

    final_results = reranker.rerank(
        question,
        final_results,
        top_k=5
    )

    MIN_RERANK_SCORE = 0.4

    if not final_results or final_results[0]["rerank_score"] < MIN_RERANK_SCORE:

        answer = "Je ne trouve pas cette information dans les documents."

    else:

        context = []

        sources = []
        seen_docs = set()

        for r in final_results:

            context.append(
                f"Document : {r['document']}\n"
                f"Contenu :\n{r['text']}"
            )

            if r["document"] and r["document"] not in seen_docs:
                seen_docs.add(r["document"])
                sources.append(r["document"])

        llm = LLMService()

        answer = llm.generate(question, context)

        # Ajouter automatiquement les sources
        if sources:
            answer += "\n\nSources :\n"
            for doc in sources:
                answer += f"- {doc}\n"

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