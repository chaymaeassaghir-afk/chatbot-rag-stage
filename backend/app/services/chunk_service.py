from app.database import SessionLocal
from app.models.chunk import Chunk
from sqlalchemy import func
from sqlalchemy import text



class ChunkService:

    def save_chunks(
        self,
        document_id,
        chunks
    ):

        db = SessionLocal()

        try:

            for chunk in chunks:

                db.add(
                    Chunk(
                        document_id=document_id,
                        chunk_id=chunk["id"],
                        text=chunk["text"],
                        length=chunk["length"],
                    )
                )

            db.commit()

        finally:

            db.close()

    def search(self, query: str, limit=5):

        db = SessionLocal()

        try:

            return (
                db.query(Chunk)
                .filter(
                    text(
                        "to_tsvector('simple', text) @@ plainto_tsquery('simple', :q)"
                    )
                )
                .params(q=query)
                .limit(limit)
                .all()
            )

        finally:
            db.close()        