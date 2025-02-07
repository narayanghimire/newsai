from sentence_transformers import SentenceTransformer


class EmbeddingService:
    model = SentenceTransformer("intfloat/multilingual-e5-large")

    @staticmethod
    async def get_embedding(text: str):
        """
        Generate embeddings locally using multilingual-e5-large.
        """
        return EmbeddingService.model.encode(text).tolist()