from openai import OpenAI
from typing import List, Dict

from app.schemas.schemas import NewsKeywordResponse, NewsSummaryResponse
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
                        "You are an AI that generates highly relevant and optimized search queries "
                        "for retrieving the most accurate news articles from News API. "
                        "Your job is to understand the user's intent, correct spelling mistakes, "
                        "and construct a well-formatted query that improves search accuracy."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Analyze the user's request and generate an optimized search query for the News API.\n"
                        "- First, **correct any spelling mistakes** in the user's input.\n"
                        "- Then, **understand the intent** behind the request. The query does not have to be an exact match but should be relevant.\n"
                        "- If the user provides a very specific topic, broaden it slightly while maintaining relevance.\n"
                        "- If the request is too broad, refine it to ensure the News API returns **accurate and relevant news**.\n\n"
                        "**Guidelines for formatting the query:**\n"
                        "- Use 'AND' between important keywords (e.g., Google AND Gulf AND America).\n"
                        "- Avoid using unnecessary punctuation like extra quotes (\").\n"
                        "- Do NOT use '+' or '-' operators (not needed for News API).\n"
                        "- If a phrase is too specific, break it into meaningful keywords.\n\n"
                        "**Return the JSON format:**\n"
                        "{\n"
                        "  \"search_query\": \"optimized query\",\n"
                        "  \"keywords\": [\"keyword1\", \"keyword2\", \"keyword3\"]\n"
                        "}\n\n"
                        f"User's request: '{prompt}'"
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
                    for item in news_data[:5]
                    if isinstance(item, dict) and 'content' in item and 'url' in item
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

                            Only summarize details that answer the user's question. Avoid unrelated information and Please avoid 
                            adding unnecessary stuff in the summary (for example: Prompt is asking english football and summary response
                            should not contain about English cricket).
                            During Summarization , it should use easy english language without using complicated and difficult words and 
                            engaging article.
                            Additionally, **explicitly list the source URLs** that were used in the summary.

                            News Articles:
                            {combined_news}

                            **Format the response as follows:**
                            Summary: <Your summary here>
                            source_urls: <List of URLs used in the summary>
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







