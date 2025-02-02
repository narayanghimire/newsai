from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    created_at = Column(DateTime, default=func.now())
    articles = relationship("SummarizedArticle", back_populates="user")


class NewsSource(Base):
    __tablename__ = "news_sources"
    source_id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), nullable=False)
    site_url = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())


class SummarizedArticle(Base):
    __tablename__ = "summarized_articles"
    summary_id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("news_sources.source_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    summarized_content = Column(Text, nullable=False)
    prompt = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="articles")
    source = relationship("NewsSource")
