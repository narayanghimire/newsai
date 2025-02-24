from abc import ABC
from typing import List, Dict
from google import genai
from google.genai import types

from app.schemas.schemas import NewsKeywordResponse, NewsSummaryResponse
from app.services.llm_service.base_llm_service import BaseLLMService
import json

class GeminiLlmService(BaseLLMService):
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def generate_news_keywords(self, prompt: str) -> NewsKeywordResponse:
        """
        Extracts a formatted search query for NewsAPI and a list of relevant keywords.
        """
        sys_instruct =(
            "You are an AI that generates highly relevant and optimized search queries "
            "for retrieving the most accurate news articles from News API. "
            "Your job is to understand the user's intent, correct spelling mistakes, "
            "and construct a well-formatted query that improves search accuracy."
            "Always return a JSON object with 'search_query' and 'keywords'.")
        contents = f"""
                        f"Analyze the user's request and generate an optimized search query for the News API.\n"
                        "- First, **correct any spelling mistakes** in the user's input.\n"
                        "- Then, **understand the intent** behind the request. The query does not have to be an exact match but should be relevant.\n"
                        "- If the user provides a very specific topic, broaden it slightly while maintaining relevance.\n"
                        "- If the request is too broad, refine it to ensure the News API returns **accurate and relevant news**.\n\n"
                        "Format it according to News API guidelines:\n"
                        "- Avoid using too many quotes (\"). Use them only for short, critical phrases.\n"
                        "- Use 'AND' between keywords (e.g., Google AND Gulf AND America).\n"
                        "- Do NOT use '+' or '-' operators (they are not needed for NewsAPI).\n"
                        "- If a phrase is too specific, break it into individual keywords.\n\n"
        f"User's request: '{prompt}'"
        **Return ONLY a valid JSON object. Do NOT include any extra text, explanations, or formatting like markdown code blocks.**  

        **Example output format:**
        {{
            "search_query": "formatted query",
            "keywords": ["keyword1", "keyword2", "keyword3"]
        }}
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0,
                    system_instruction=sys_instruct,
                    response_mime_type="application/json",
                    response_schema=NewsKeywordResponse
                )
            )
            response_json = json.loads(response.text)
            return NewsKeywordResponse(**response_json)
        except Exception as e:
            print(f"Error in generate_news_keywords: {e}")
            return NewsKeywordResponse(

                search_query="",
                keywords=[]
            )


    def generate_summary(self, news_data: List[Dict], prompt: str) -> NewsSummaryResponse:
        """
        Generate a structured summary from a list of news articles using Gemini.
        Ensures the summary includes and acknowledges only the sources actually used.
        """
        try:
            combined_news = "\n\n".join(
                [
                    f"Description: {item['content']}\nSource: {item['url']}"
                    for item in news_data[:5]
                    if isinstance(item, dict) and 'content' in item and 'url' in item
                ]
            )

            if not combined_news.strip():
                return NewsSummaryResponse(
                    summary="No news content available to summarize.",
                    source_urls=[]
                )
            sys_instruct = ("You are an AI that summarizes news articles concisely and accurately. "
                            "Ensure the summary is informative, engaging, and retains key details from the articles. "
                            "The summary must explicitly reference and list the source URLs it is based on."
                            )
            contents = f"""
                        Summarize the following news articles, ensuring the summary is directly relevant to this user query: 
                        '{prompt}'
                        
                        Only summarize details that answer the user's question. Avoid unrelated information and Please avoid 
                        adding unnecessary stuff in summary (for example: Prompt is asking english football and summary response
                        should not contain about English cricket).
                        Use simple and engaging English without complicated words.

                        Additionally, **explicitly list the source URLs** that were used in the summary.

                        News Articles:
                        {combined_news}

                        **Format the response as follows (JSON format):**
                        {{
                          "summary": "Your summary here",
                          "source_urls": ["url1", "url2"]
                        }}
                    """

            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    system_instruction=sys_instruct,
                    response_mime_type="application/json",
                    response_schema=NewsSummaryResponse
                )
            )
            response_json = json.loads(response.text)
            return NewsSummaryResponse(**response_json)

        except Exception as e:
            print(f"Error generating summary: {e}")
            return NewsSummaryResponse(
                summary="An error occurred while generating the summary. Please try again later.",
                source_urls=[]
            )
