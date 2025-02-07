from itertools import count

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.model.models import SummarizedArticle, NewsSource, User
from app.schemas.schemas import NewsRequest, NewsSummaryResponse
from app.services.llm_manager import LLMManager
from app.services.news_service import NewsService
from fastapi import Request, Response

from app.services.rag_service.rag_service import RagService
from routers.user_router import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/available-llms")
async def get_available_llms():
    """
        Fetch available LLM models.
    """
    return {"models": LLMManager.list_available_models()}

@router.get("/llm/selected")
async def get_selected_llm(request: Request):
    return request.cookies.get("selected_llm", "openai")

@router.post("/llm/select/{model_name}")
async def set_llm(model_name: str, response: Response):
    """
    Change the LLM model in session.
    """
    available_models = LLMManager.list_available_models()
    if model_name not in available_models:
        raise HTTPException(status_code=400, detail="Invalid LLM model selection")

    response.set_cookie(key="selected_llm", value=model_name)
    return {"message": f"LLM changed to {model_name}"}


@router.post("/generate-news")
async def generate_news(
        request: NewsRequest,
        selected_llm: str = Depends(get_selected_llm),
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    llm_service = LLMManager.get_llm(selected_llm)

    news_keyword_response = llm_service.generate_news_keywords(request.prompt)

    news_data = await NewsService.fetch_news_from_newsapi(news_keyword_response)

    await RagService.store_new_articles_in_vector_db(news_data, db)
    similar_articles = await RagService.query_similar_articles(news_keyword_response, db)
    if not similar_articles:
        raise HTTPException(status_code=404, detail="No relevant news found.")

    news_summary_response = llm_service.generate_summary(similar_articles, request.prompt)
    await save_article_to_db(news_summary_response, db, user, request.prompt)

    return {
        "summary": news_summary_response.summary,
        "source": news_summary_response.source_urls
    }


async def save_article_to_db(news_summary_response: NewsSummaryResponse, db: Session, user, prompt: str):
    site_url = ";".join(news_summary_response.source_urls)
    news_source = NewsSource(source_name=prompt, site_url=site_url)
    db.add(news_source)
    db.commit()
    db.refresh(news_source)

    summarized_article = SummarizedArticle(
        user_id=user.user_id,
        source_id=news_source.source_id,
        summarized_content=news_summary_response.summary,
        prompt=prompt,
    )
    db.add(summarized_article)
    db.commit()
