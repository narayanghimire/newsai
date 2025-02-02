from openai import OpenAI
from typing import List, Dict

from app.schemas.schemas import NewsKeywordResponse, NewsSummaryResponse
from app.services.llm_service.base_llm_service import BaseLLMService


class OpenAILLMService(BaseLLMService):

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_news_keywords(self, prompt: str) -> NewsKeywordResponse:
        """
        Extracts both a formatted search query for NewsAPI and a list of relevant keywords for RAG.
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
                        "- Use quotes (\") for exact matches (e.g., \"Gulf of America\").\n"
                        "- Use '+' before must-have words (e.g., +Google +Gulf).\n"
                        "- Use '-' before words to exclude (e.g., -oldname).\n"
                        "- Use 'AND', 'OR', 'NOT' logically (e.g., Google AND (Gulf OR America) NOT renaming).\n\n"
                        "Also, extract a **list of relevant keywords** from the prompt to be used for similarity search in RAG.\n"
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
        Returns a `NewsSummaryResponse` object.
        """
        try:
            # Combine all news content
            combined_news = "\n\n".join(
                [
                    f"Description: {item['content']}" if isinstance(item,
                                                                         dict) and 'content' in item else item
                    for item in news_data
                ]
            )

            # Check if the combined news content is empty
            if not combined_news.strip():
                return NewsSummaryResponse(summary="No news content available to summarize.")


            # Call GPT model to generate a summary
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                temperature=0.2,
                messages=[
                    {
                        "role": "developer",
                        "content": (
                            "You are an AI that summarizes news articles concisely and accurately "
                            "and ensure the summary is informative, engaging, and retains key details from the articles"
                        )
                    },
                    {
                        "role": "user",
                        "content": f"""
                            Summarize the following news articles, ensuring the summary is directly relevant to this user query: 
                            '{prompt}'

                            Only summarize details that answer the user's question. Avoid unrelated information.

                            News Articles:  
                            {combined_news}
                        """
                    }

                ],
                response_format=NewsSummaryResponse,
            )

            return completion.choices[0].message.parsed

        except Exception as e:
            print(f"Error generating summary: {e}")
            return NewsSummaryResponse(
                summary="An error occurred while generating the summary. Please try again later.")