from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:

    def __init__(self):

        self.model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

    def dimension(self):
        return self.model.get_sentence_embedding_dimension()

    def encode(self, chunks):

        return self.model.encode(
            chunks,
            convert_to_numpy=True
        )