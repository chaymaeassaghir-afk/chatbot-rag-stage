from sentence_transformers import CrossEncoder


class RerankerService:
    _model = None

    def __init__(self):

        if RerankerService._model is None:

            print("Chargement du reranker...")

            RerankerService._model = CrossEncoder(
                "BAAI/bge-reranker-base"
            )
        self.model = RerankerService._model

    def rerank(self, query, results, top_k=5):

        if not results:
            return []

        pairs = [
            (query, result["text"])
            for result in results
        ]

        scores = self.model.predict(pairs)

        for result, score in zip(results, scores):
            result["rerank_score"] = float(score)

        results.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return results[:top_k]