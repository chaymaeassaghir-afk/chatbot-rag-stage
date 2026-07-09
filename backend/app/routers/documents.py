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


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

from app.dependencies.auth import require_admin
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

@router.post("/upload")
def upload_pdf(file: UploadFile, current_user=Depends(require_admin)):

    path = PDFService.save(file)

    text = PDFService.extract_text(path)
    chunks = Chunker.split(text)
    texts = [chunk["text"] for chunk in chunks]

    generator = EmbeddingGenerator()
    vectors = generator.encode(texts)

    from app.services.qdrant_service import QdrantService
    # Temporaire (plus tard il viendra de PostgreSQL)
    document_id = 1
    document_name = file.filename

    qdrant = QdrantService()

    qdrant.store_chunks(
        document_id=document_id,
        document_name=document_name,
        chunks=chunks,
        vectors=vectors
    )

    return {
        "filename": file.filename,
        "characters": len(text),
        "chunks": len(chunks),
        "embedding_dimension": len(vectors[0]),
        "first_chunk": chunks[0]["text"],
        "first_values": vectors[0][:10].tolist()
    }

from app.dependencies.auth import require_user
@router.get("/search")
def search( query: str,current_user=Depends(require_user)):

    qdrant = QdrantService()

    results = qdrant.search(query)

    chunks = []

    sources = []

    for result in results:

        chunks.append(result.payload["text"])

        sources.append({
            "document": result.payload["document_name"],
            "chunk_id": result.payload["chunk_id"],
            "score": result.score
        })

    llm = LLMService()

    answer = llm.generate(query, chunks)

    return {
        "question": query,
        "answer": answer,
        "sources": sources
    }