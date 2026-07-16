from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository
from app.services.qdrant_service import QdrantService

class DocumentService:

    @staticmethod
    def create_document(db: Session, filename: str):

        return DocumentRepository.create(db, filename)


    @staticmethod
    def list_documents(db: Session):

        return DocumentRepository.get_all(db)

    @staticmethod
    def delete_document(db: Session, document_id: int):
        
        qdrant = QdrantService()

        qdrant.delete_document(document_id)

        return DocumentRepository.delete(
            db,
            document_id
        )    