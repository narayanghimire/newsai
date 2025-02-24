import json
from groq import Groq
from typing import List, Dict
from app.schemas.schemas import NewsKeywordResponse, NewsSummaryResponse
from app.services.llm_service.base_llm_service import BaseLLMService

class GroqLlmService(BaseLLMService):
    MAX_ARTICLES = 5
    MAX_TOKENS = 5000
    MAX_CONTENT_LENGTH = 500

    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def generate_news_keywords(self, prompt: str) -> NewsKeywordResponse:
        """
        Extracts a formatted search query for NewsAPI and a list of relevant keywords.
        """
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0,
            messages=[
                {"role": "system", "content": (
                    "You are an AI that generates highly relevant and optimized search queries "
                    "for retrieving the most accurate news articles from News API. "
                    "Your job is to understand the user's intent, correct spelling mistakes, "
                    "and construct a well-formatted query that improves search accuracy."
                    "Return a JSON with 'search_query' and 'keywords'. No extra text or formatting."
                )},
                {"role": "user", "content": (
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
                    "**Return the JSON object:**\n"
                    "{\n"
                    "  \"search_query\": \"optimized query\",\n"
                    "  \"keywords\": [\"keyword1\", \"keyword2\", \"keyword3\"]\n"
                    "}\n\n"
                    f"User's request: '{prompt}'"
                )}
            ],
        )

        response_json = json.loads(completion.choices[0].message.content)
        return NewsKeywordResponse(**response_json)

    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimate of token count. (1 word ≈ 1 token)
        """
        return len(text.split())

    def generate_summary(self, news_data: List[Dict], prompt: str) -> NewsSummaryResponse:
        """
        Generate a structured summary from a list of news articles.
        """
        try:
            selected_articles = news_data[:self.MAX_ARTICLES]  # Start with max articles
            token_budget = self.MAX_TOKENS - self.estimate_tokens(prompt)
            article_summaries = []

            for article in selected_articles:
                if not isinstance(article, dict) or 'content' not in article or 'url' not in article:
                    continue

                content = article['content'][:self.MAX_CONTENT_LENGTH]
                tokens = self.estimate_tokens(content)

                if token_budget - tokens < 0:
                    break

                article_summaries.append(f"Description: {content}\nSource: {article['url']}")
                token_budget -= tokens

            if not article_summaries:
                return NewsSummaryResponse(
                    summary="The news articles are too lengthy to process. Try again with fewer articles.",
                    source_urls=[]
                )

            combined_news = "\n\n".join(article_summaries)

            # Call GPT model to generate a structured response
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=0.2,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI that summarizes news articles concisely and accurately. "
                            "Use simple, engaging language. "
                            "Return a JSON with 'summary' and 'source_urls'. No extra formatting."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"""
                            Summarize the following news articles relevant to this query: 
                            '{prompt}'

                            - Use simple, easy-to-understand English.
                            - Keep the summary concise but informative.
                            - Only summarize details that answer the prompt question
                            - Explicitly list the sources used.

                            News Articles:
                            {combined_news}

                            Return JSON:
                            {{
                              "summary": "<Your summary here>",
                              "source_urls": ["<List of URLs used in the summary>"]
                            }}
                        """
                    }
                ],
            )

            response_json = json.loads(completion.choices[0].message.content)
            return NewsSummaryResponse(**response_json)
        except Exception as e:
            print(f"Error generating summary: {e}")
            return NewsSummaryResponse(
                summary="An error occurred while generating the summary. Please try again later.",
                source_urls=[]
            )
