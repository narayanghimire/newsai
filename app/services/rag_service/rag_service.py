from typing import List, Dict

from app.schemas.schemas import NewsKeywordResponse
from app.services.article_database_service import ArticleDatabaseService
from app.services.rag_service.embedding_service import EmbeddingService
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config import news_index
from app.database.database import SessionLocal

router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RagService:

    @staticmethod
    async def store_new_articles_in_vector_db(news_data: List[dict], db: Session):
        """
        Store news articles by saving embeddings in Pinecone and full content in a local database.
        """
        existing_ids = RagService.get_existing_news_ids([article["url"] for article in news_data])

        vectors = []
        for article in news_data:
            article_url = article["url"]

            if article_url in existing_ids:
                continue

            embedding = await EmbeddingService.get_embedding(article["content"])
            ArticleDatabaseService.store_article(article, db)
            vectors.append(
                (
                    article_url,
                    embedding,
                    {
                        "title": article["title"],
                        "publishedAt": article["publishedAt"],
                        "url": article_url,
                    }
                )
            )

        if vectors:
            news_index.upsert(vectors)

    @staticmethod
    def get_existing_news_ids(urls: List[str]):
        """
        Check which news articles are already stored in the vector database.
        Returns a set of existing news article URLs.
        """
        existing_ids = set()
        for url in urls:
            results = news_index.query(id=url, top_k=1, include_metadata=True)
            if results and results.get("matches"):
                existing_ids.add(url)

        return existing_ids

    @staticmethod
    async def query_similar_articles(
            news_keyword: NewsKeywordResponse,
            db: Session = Depends(get_db),
            min_relevance: float = 0.7
    ) -> List[Dict]:
        """
        Retrieve similar articles using embeddings and fetch full content from the database.
        """
        if not news_keyword.keywords:
            return []

        keyword_embedding = await EmbeddingService.get_embedding(", ".join(news_keyword.keywords))
        results = news_index.query(vector=keyword_embedding, top_k=5, include_metadata=True)

        relevant_articles = []
        for r in results["matches"]:
            if r["score"] < min_relevance:
                continue

            full_article = ArticleDatabaseService.get_article(r["metadata"]["url"], db)
            if not full_article:
                continue

            relevant_articles.append(
                {
                    "title": full_article.title,
                    "content": full_article.content,
                    "publishedAt": full_article.published_at,
                    "url": full_article.url,
                    "score": r["score"]
                }
            )

        return relevant_articles
