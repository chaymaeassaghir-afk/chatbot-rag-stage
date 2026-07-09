from app.rag.embeddings import EmbeddingGenerator
from qdrant_client.models import PointStruct

import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)

class QdrantService:

    def __init__(self):

        self.client = QdrantClient(
            host="localhost",
            port=6333
        )

        self.collection_name = "documents"
        self.embedding = EmbeddingGenerator()

    def create_collection(self):
        
        collections = self.client.get_collections().collections

        names = [c.name for c in collections]
        embedding_generator = EmbeddingGenerator()
        dimension = embedding_generator.dimension()

        if self.collection_name not in names:

            self.client.create_collection(
                collection_name=self.collection_name,

                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE
                )
            )

            print("Collection créée.")

        else:

            print("Collection déjà existante.")

    def store_chunks(self, document_id, document_name, chunks, vectors):

        points = []

        for chunk, vector in zip(chunks, vectors):

            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),

                    vector=vector.tolist(),

                    payload={
                        "document_id": document_id,
                        "document_name": document_name,
                        "chunk_id": chunk["id"],
                        "text": chunk["text"],
                        "length": chunk["length"]
                    }
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        print(f"{len(points)} chunks enregistrés dans Qdrant.")

    def search(self, query, limit=5):

        vector = self.embedding.encode([query])[0]

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector.tolist(),
            limit=limit
        )

        return results.points   