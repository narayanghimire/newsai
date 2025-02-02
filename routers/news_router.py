from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.model.models import SummarizedArticle, NewsSource, User
from app.schemas.schemas import NewsRequest
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
    print(f"SElECTED LLM :" + selected_llm)
    newsKeywordResponse = llm_service.generate_news_keywords(request.prompt)
    similar_articles = await RagService.query_similar_articles(request.prompt)
    news_data, source_urls = await NewsService.fetch_news_from_newsapi(newsKeywordResponse)

    if not news_data and not similar_articles:
        raise HTTPException(status_code=404, detail="No relevant news found.")

    all_news_data = news_data + [article["content"] for article in similar_articles]
    summarized_text = llm_service.generate_summary(all_news_data, request.prompt)

    await save_article_to_db(source_urls, summarized_text, db, user, request.prompt)
    return {"summary": summarized_text.summary}


async def save_article_to_db(source_urls, summarized_content, db: Session, user, prompt: str):
    site_url = ";".join(source_urls) if isinstance(source_urls, list) else ""
    news_source = NewsSource(source_name=prompt, site_url=site_url)
    db.add(news_source)
    db.commit()
    db.refresh(news_source)

    summarized_article = SummarizedArticle(
        user_id=user.user_id,
        source_id=news_source.source_id,
        summarized_content=summarized_content.summary,
        prompt=prompt,
    )
    db.add(summarized_article)
    db.commit()
