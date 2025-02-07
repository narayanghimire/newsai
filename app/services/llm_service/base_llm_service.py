from abc import ABC, abstractmethod
from typing import List, Dict
from app.schemas.schemas import NewsKeywordResponse, NewsSummaryResponse, ExtractedRawHtmlResponse


class BaseLLMService(ABC):

    @abstractmethod
    def generate_news_keywords(self, prompt: str) -> NewsKeywordResponse:
        """ Extracts relevant search queries and keywords for news retrieval. """
        pass

    @abstractmethod
    def generate_summary(self, news_data: List[Dict], prompt: str) -> NewsSummaryResponse:
        """ Summarizes the collected news articles. """
        pass
