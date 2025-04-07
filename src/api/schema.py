from pydantic import BaseModel, Field


class IntervalQuery(BaseModel):
    minutes: int = Field(..., ge=1, description="Interval in minutes")


class ArticleQuery(BaseModel):
    article_url: str


class ArticleDetailQuery(BaseModel):
    id: int


class SearchQuery(BaseModel):
    keyword: str
