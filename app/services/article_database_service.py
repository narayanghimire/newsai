from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from app.model.models import NewsArticle


class ArticleDatabaseService:

    @staticmethod
    def store_article(article_data: dict, db: Session):
        """
        Stores full article content in SQLite synchronously.
        """
        article_url = article_data.get("url")
        if not article_url or not isinstance(article_url, str):
            raise ValueError("Invalid or missing article URL")

        existing_article = db.execute(
            select(NewsArticle).filter(NewsArticle.url == article_url)
        ).scalar_one_or_none()

        if existing_article:
            return existing_article

        published_at_str = article_data.get("publishedAt")
        published_at = None
        if published_at_str:
            try:
                published_at = datetime.fromisoformat(published_at_str)
            except ValueError:
                published_at = datetime.utcnow()

        new_article = NewsArticle(
            url=article_url,
            title=article_data["title"],
            content=article_data["content"],
            published_at=published_at
        )

        db.add(new_article)
        db.commit()
        db.refresh(new_article)
        return new_article

    @staticmethod
    def get_article(article_url: str, db: Session):
        """
        Retrieve a full article from the database synchronously.
        """
        result = db.execute(
            select(NewsArticle).filter(NewsArticle.url == article_url)
        )
        return result.scalar_one_or_none()
