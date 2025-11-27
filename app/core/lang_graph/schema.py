from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class Article(BaseModel):
    title: str
    url: HttpUrl
    sentiment: float


class FinalReport(BaseModel):
    coin_name: str
    days: int
    top_articles: List[Article]
    average_sentiment: float
    sentiment_trend: str


class ScrapedArticle(BaseModel):
    url: str
    content: str


class AnalyzedArticle(BaseModel):
    url: str
    sentiment: float
    content: str


class SentimentAnalysisState(BaseModel):
    coin_name: str
    days: int
    search_results: List[str] = []
    scraped_articles: List[ScrapedArticle] = []
    filtered_articles: List[ScrapedArticle] = []
    analyzed_articles: List[AnalyzedArticle] = []
    final_report: Optional[FinalReport] = None

