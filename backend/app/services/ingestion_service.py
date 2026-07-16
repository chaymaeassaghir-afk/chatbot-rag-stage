from sqlalchemy.orm import Session

from app.services.s3_service import S3Service
from app.services.document_service import DocumentService
from app.services.qdrant_service import QdrantService

from app.rag.chunker import Chunker
from app.rag.embeddings import EmbeddingService

from app.utils.extract_text import extract_text


class IngestionService:

    def __init__(self):

        self.s3 = S3Service()
        self.chunker = Chunker()
        self.embedding = EmbeddingService()
        self.qdrant = QdrantService()

    def ingest_bucket(self, db: Session):

        files = self.s3.list_files()

        for file in files:

            filename = file["Key"]

            print(f"Ingestion : {filename}")

            binary = self.s3.download_file(filename)

            text = extract_text(
                filename,
                binary
            )

            document = DocumentService.create_document(
                db=db,
                filename=filename,
                content=text
            )

            chunks = self.chunker.split(text)

            for index, chunk in enumerate(chunks):

                vector = self.embedding.encode(chunk)

                self.qdrant.add_document(
                    document_id=document.id,
                    chunk_id=index,
                    text=chunk,
                    embedding=vector
                )

            print(f"{filename} terminé.")