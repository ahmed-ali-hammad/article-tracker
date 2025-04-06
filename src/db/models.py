from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Article(Base):
    __tablename__ = "article"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topline = Column(String, nullable=False)
    headline = Column(String, nullable=False)
    short_text = Column(Text, nullable=False)
    article_url = Column(String, nullable=False, unique=True)

    details = relationship("ArticleDetail", back_populates="article")


class ArticleDetail(Base):
    __tablename__ = "article_detail"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("article.id"), nullable=False)
    topline = Column(String, nullable=False)
    headline = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(Integer, nullable=False)

    article = relationship("Article", back_populates="details")
