from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Table, func
from sqlalchemy.orm import relationship
from app.database.database import Base

# Association Table for Many-to-Many Relationship
summarized_article_news_article = Table(
    "summarized_article_news_article",
    Base.metadata,
    Column("summary_id", Integer, ForeignKey("summarized_articles.summary_id"), primary_key=True),
    Column("article_id", Integer, ForeignKey("news_articles.article_id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    created_at = Column(DateTime, default=func.now())

    articles = relationship("SummarizedArticle", back_populates="user")

class NewsArticle(Base):
    __tablename__ = "news_articles"
    article_id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

class SummarizedArticle(Base):
    __tablename__ = "summarized_articles"
    summary_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    summarized_content = Column(Text, nullable=False)
    prompt = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    llm_model = Column(String(50), nullable=False)  # Store LLM Model Name

    user = relationship("User", back_populates="articles")
    articles = relationship("NewsArticle", secondary=summarized_article_news_article, backref="summaries")