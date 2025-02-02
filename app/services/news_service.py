import asyncio
import os

import httpx
from dotenv import load_dotenv

from app.model.models import NewsSource
from sqlalchemy.orm import Session
from app.model.models import SummarizedArticle
from app.schemas.schemas import NewsKeywordResponse
from app.services.rag_service.rag_service import RagService

load_dotenv()

class NewsService:
    API_KEY = os.getenv("NEWS_API_KEY")
    BASE_URL = "https://newsapi.org/v2/everything"

    @staticmethod
    async def fetch_news_from_newsapi(prompt_keywords: NewsKeywordResponse):
        """
        Fetches news articles from NewsAPI based on extracted keywords.
        Then, it scrapes each article's URL to retrieve full text.
        Returns:
        - news_data: List of articles with full content.
        - source_urls: List of original article URLs.
        """
        params = {
            "q": prompt_keywords.search_query,
            "pageSize": 3,
            "apiKey": NewsService.API_KEY,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(NewsService.BASE_URL, params=params)
                response.raise_for_status()

                data = response.json()
                articles = data.get("articles", [])

                if not articles:
                    print("No articles found.")
                    return [], []

                source_urls = [article["url"] for article in articles]
                full_contents = await asyncio.gather(
                    *[NewsService.scrape_full_content(url) for url in source_urls]
                )

                news_data = [
                    {
                        "content": full_text,
                    }
                    for article, full_text in zip(articles, full_contents)
                ]
                await RagService.store_news_in_vector_db(news_data, source_urls)

                return news_data, source_urls

        except httpx.RequestError as e:
            print(f"Error while fetching news: {e}")
            return [], []
        except KeyError as e:
            print(f"Error processing news data: {e}")
            return [], []

    @staticmethod
    async def scrape_full_content(article_url: str) -> str:
        """
        Scrapes full news content from the article URL.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(article_url, timeout=10)
                if response.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, "html.parser")
                    paragraphs = soup.find_all("p")
                    return " ".join(p.get_text() for p in paragraphs)
                else:
                    print(f"Failed to fetch article content from {article_url}")
                    return "Content not available."
        except httpx.RequestError as e:
            print(f"Error scraping article content from {article_url}: {e}")
            return "Content not available."


    def get_summarized_articles(user_id: int, db: Session):
        summaries = (
            db.query(SummarizedArticle)
            .join(NewsSource)
            .filter(SummarizedArticle.user_id == user_id)
            .all()
        )

        return [
            {
                "summary_id": summary.summary_id,
                "summarized_content": summary.summarized_content,
                "prompt": summary.prompt,
                "created_at": summary.created_at,
            }
            for summary in summaries
        ]


