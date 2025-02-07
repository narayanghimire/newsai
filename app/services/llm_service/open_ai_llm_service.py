import httpx
from bs4 import BeautifulSoup, Comment
from openai import OpenAI
from typing import List, Dict

from app.schemas.schemas import NewsKeywordResponse, NewsSummaryResponse, ExtractedRawHtmlResponse
from app.services.llm_service.base_llm_service import BaseLLMService

class OpenAILLMService(BaseLLMService):

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_news_keywords(self, prompt: str) -> NewsKeywordResponse:
        """
        Extracts a formatted search query for NewsAPI and a list of relevant keywords.
        """
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {
                    "role": "developer",
                    "content": (
                        "You are an AI that extracts **highly relevant search queries** "
                        "for news articles. Always return a JSON object with 'search_query' and 'keywords'."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Extract the most relevant search query for the News API from this prompt: '{prompt}'.\n"
                        "Format it according to News API guidelines:\n"
                        "- Avoid using too many quotes (\"). Use them only for short, critical phrases.\n"
                        "- Use 'AND' between keywords (e.g., Google AND Gulf AND America).\n"
                        "- Do NOT use '+' or '-' operators (they are not needed for NewsAPI).\n"
                        "- If a phrase is too specific, break it into individual keywords.\n\n"
                        "Return the JSON format:\n"
                        "{\n"
                        "  \"search_query\": \"formatted query\",\n"
                        "  \"keywords\": [\"keyword1\", \"keyword2\", \"keyword3\"]\n"
                        "}"
                    )
                }
            ],
            response_format=NewsKeywordResponse,
        )

        return completion.choices[0].message.parsed

    def generate_summary(self, news_data: List[Dict], prompt: str) -> NewsSummaryResponse:
        """
        Generate a structured summary from a list of news articles using GPT.
        Ensures the summary includes and acknowledges only the sources actually used.
        """
        try:
            # Prepare news content with URLs
            combined_news = "\n\n".join(
                [
                    f"Description: {item['content']}\nSource: {item['url']}"
                    if isinstance(item, dict) and 'content' in item and 'url' in item
                    else item
                    for item in news_data
                ]
            )

            # Check if the combined news content is empty
            if not combined_news.strip():
                return NewsSummaryResponse(
                    summary="No news content available to summarize.",
                    source_urls=[]
                )

            # Call GPT model to generate a structured response
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                temperature=0.2,
                messages=[
                    {
                        "role": "developer",
                        "content": (
                            "You are an AI that summarizes news articles concisely and accurately. "
                            "Ensure the summary is informative, engaging, and retains key details from the articles. "
                            "The summary must explicitly reference and list the source URLs it is based on."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"""
                            Summarize the following news articles, ensuring the summary is directly relevant to this user query: 
                            '{prompt}'

                            Only summarize details that answer the user's question. Avoid unrelated information.
                            During Summarization , it should use easy english language without using complicated and difficult words and 
                            engaging article.
                            Additionally, **explicitly list the source URLs** that were used in the summary.

                            News Articles:
                            {combined_news}

                            **Format the response as follows:**
                            Summary: <Your summary here>
                            Sources: <List of URLs used in the summary>
                        """
                    }
                ],
                response_format=NewsSummaryResponse,
            )

            return  completion.choices[0].message.parsed

        except Exception as e:
            print(f"Error generating summary: {e}")
            return NewsSummaryResponse(
                summary="An error occurred while generating the summary. Please try again later.",
                source_urls=[]
            )







