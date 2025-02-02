from typing import List

from app.services.rag_service.embedding_service import EmbeddingService
from config import news_index


class RagService:

    @staticmethod
    async def store_news_in_vector_db(news_data, source_urls):
        """
        Store news articles in Pinecone with embeddings.
        """
        for article, source in zip(news_data, source_urls):
            embedding = await EmbeddingService.get_embedding(article["content"])
            news_index.upsert([(source, embedding, {"content": article["content"], "source": source})])

    @staticmethod
    async def query_similar_articles(prompt: str):
        """
            Retrieve similar articles using Pinecone.
        """
        query_text = f"Find recent news related to: {prompt}"
        query_embedding = await EmbeddingService.get_embedding(query_text)
        results = news_index.query(vector=query_embedding, top_k=5, include_metadata=True)
        return [{"content": r["metadata"]["content"], "source": r["metadata"]["source"]} for r in results["matches"]]

