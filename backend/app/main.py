from fastapi import FastAPI
from app.routers import documents
from app.routers import auth
from app.database import Base, engine

import app.models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Assistant RAG",
    version="1.0.0",
    description="API du projet de stage"
)
from app.services.qdrant_service import QdrantService

service = QdrantService()
service.create_collection()

app.include_router(documents.router)
app.include_router(auth.router)

from app.routers import chat
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "API du projet RAG en cours d'exécution"}