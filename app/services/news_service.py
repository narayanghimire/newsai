import asyncio
import os
import urllib.parse
from datetime import datetime, timedelta

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException
from newspaper import Article

from app.model.models import NewsSource
from sqlalchemy.orm import Session
from app.model.models import SummarizedArticle
from app.schemas.schemas import NewsKeywordResponse

load_dotenv()

class NewsService:
    API_KEY = os.getenv("NEWS_API_KEY")
    BASE_URL = "https://newsapi.org/v2/everything"

    @staticmethod
    async def fetch_news_from_newsapi(prompt_keywords):
        """
        Fetches news articles from NewsAPI based on extracted keywords.
        Then, it processes each article's URL to retrieve full content.
        Returns:
        - List of news articles with full content and metadata.
        """
        today = datetime.utcnow()
        from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")

        params = {
            "q": prompt_keywords.search_query,
            "sortBy": "relevancy",
            "from": from_date,
            "language": "en",
            "pageSize": 20,
            "apiKey": NewsService.API_KEY,
        }
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(NewsService.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

                articles = data.get("articles", [])
                if not articles:
                    print("No articles found.")
                    return []

                # Extract content asynchronously for all articles
                extracted_results = await asyncio.gather(
                    *[NewsService.extract_news(article["url"]) for article in articles]
                )

                news_data = []
                for article, content in zip(articles, extracted_results):
                    news_entry = {
                        "content": content if content else "Content extraction failed.",
                        "title": article.get("title", ""),
                        "url": article.get("url", ""),
                        "publishedAt": article.get("publishedAt", "")
                    }
                    news_data.append(news_entry)

                return news_data

        except Exception as e:
            print(f"Error while fetching news: {e}")
            return []

    @staticmethod
    async def extract_news(url: str):
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                }
                response = await client.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                html_content = response.text

            # Parse article content
            article = Article(url)
            article.download(input_html=html_content)
            article.parse()

            return article.text

        except httpx.HTTPStatusError as e:
            print(f"HTTP error {e.response.status_code} for URL: {url}")
            return None
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None

    @staticmethod
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
