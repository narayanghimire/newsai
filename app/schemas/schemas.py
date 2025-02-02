from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base User Schema
class UserBase(BaseModel):
    username: str
    email: str
    role: Optional[str] = "user"

class UserCreate(UserBase):
    password: str

class NewsKeywordResponse(BaseModel):
    """Represents the structured response containing extracted keywords."""
    search_query: str
    keywords: List[str]

class NewsSummaryResponse(BaseModel):
    """Represents the structured response containing extracted keywords."""
    summary: str

class NewsRequest(BaseModel):
    prompt: str

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# NewsSource Schema
class NewsSourceBase(BaseModel):
    source_name: str
    site_url: str  # Corrected from api_url to site_url

class NewsSourceCreate(NewsSourceBase):
    pass

class NewsSourceResponse(NewsSourceBase):
    source_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# SummarizedArticle Schema
class SummarizedArticleBase(BaseModel):
    source_id: int
    user_id: int
    summarized_content: str
    prompt: str

class SummarizedArticleCreate(SummarizedArticleBase):
    pass

class SummarizedArticleResponse(SummarizedArticleBase):
    summary_id: int
    created_at: datetime

    class Config:
        from_attributes = True
