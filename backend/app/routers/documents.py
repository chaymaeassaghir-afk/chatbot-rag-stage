from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import Query
from app.database import get_db
from app.schemas.document import DocumentCreate, DocumentResponse
from app.services.document_service import DocumentService
from app.services.qdrant_service import QdrantService
from fastapi import UploadFile
from app.services.pdf_service import PDFService
from app.rag.chunker import Chunker
from app.rag.embeddings import EmbeddingGenerator
from app.services.llm_service import LLMService
from app.dependencies.auth import get_current_user
from app.services.chunk_service import ChunkService 
from app.services.document_service import DocumentService
from app.services.reranker_service import RerankerService
from app.dependencies.auth import require_user, require_admin

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

@router.post("/", response_model=DocumentResponse)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):

    return DocumentService.create_document(
        db,
        document.filename
    )


@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db)
):

    return DocumentService.list_documents(db)

from fastapi import HTTPException
import traceback

@router.post("/upload")
def upload_pdf(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    try:
        path = PDFService.save(file)

        text = PDFService.extract_text(path)

        document = DocumentService.create_document(
            db,
            file.filename
        )

        chunks = Chunker.split(text)
        texts = [chunk["text"] for chunk in chunks]

        generator = EmbeddingGenerator()
        vectors = generator.encode(texts)

        chunk_service = ChunkService()

        chunk_service.save_chunks(
            document.id,
            chunks
        )

        qdrant = QdrantService()

        qdrant.store_chunks(
            document_id=document.id,
            document_name=document.filename,
            chunks=chunks,
            vectors=vectors
        )

        return {
            "filename": file.filename
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


import time
@router.get("/search")
def search(
    query: str,
    current_user=Depends(require_user)
):

    print("=" * 50)
    print("Nouvelle requête")
    print("Question :", query)

    qdrant = QdrantService()
    chunk_service = ChunkService()

    # Recherche sémantique
    semantic_results = qdrant.search(query, limit=5)
    # Recherche full-text
    keyword_results = chunk_service.search(query, limit=5)
   
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

    reranker = RerankerService()
    
    final_results = reranker.rerank(
        query,
        final_results,
        top_k=5
    )

    MIN_RERANK_SCORE = 0.4

    if not final_results or final_results[0]["rerank_score"] < MIN_RERANK_SCORE:

        return {
            "question": query,
            "answer": "Je ne trouve pas cette information dans les documents.",
            "sources": []
        }
    chunks = [r["text"] for r in final_results]

    sources = []

    for r in final_results:

        sources.append({
            "document_id": r["document_id"],
            "document": r["document"],
            "chunk_id": r["chunk_id"],
            "score": r["score"],
            "retrieval": r["source"]
        })
      
    
    print("\n===== CONTEXTE ENVOYÉ AU LLM =====")

    for i, c in enumerate(chunks, 1):
        print(f"\n--- Chunk {i} ---")
        print(c)

    llm = LLMService()
    answer = llm.generate(query, chunks)
    # Récupérer les documents uniques
    documents = []
    seen = set()

    for s in sources:
        if s["document"] and s["document"] not in seen:
            seen.add(s["document"])
            documents.append(s["document"])

    # Ajouter les sources à la réponse
    if documents:
        answer += "\n\nSources :\n"
        for doc in documents:
            answer += f"- {doc}\n"
    return {
        "question": query,
        "answer": answer,
        #"sources": sources
    }

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):

    deleted = DocumentService.delete_document(
        db,
        document_id
    )

    if not deleted:

        return {
            "message": "Document introuvable."
        }

    return {
        "message": "Document supprimé avec succès."
    }
