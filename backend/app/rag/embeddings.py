from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    _model = None
    def __init__(self):
        if EmbeddingGenerator._model is None:
            EmbeddingGenerator._model = SentenceTransformer(
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
        self.model = EmbeddingGenerator._model    


    def dimension(self):
        return self.model.get_sentence_embedding_dimension()

    def encode(self, chunks):

        return self.model.encode(
            chunks,
            convert_to_numpy=True
        )