from app.core.lang_graph.schema import SentimentAnalysisState, ScrapedArticle, AnalyzedArticle, FinalReport, Article

from typing import Dict
import requests
from bs4 import BeautifulSoup
from langchain_ollama import OllamaLLM
import numpy as np

ollama_llm = OllamaLLM(model="llama3.1:8b", temperature=0)

def search_news(state: SentimentAnalysisState) -> Dict:
    query = f"{state.coin_name} cryptocurrency news last {state.days} days"
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey=9b5455fab616452d95eebe6181d08a05"

    try:
        response = requests.get(url).json()
        links = [a["url"] for a in response.get("articles", [])]
    except Exception:
        links = []

    return {"search_results": links}

def scrape_articles(state: SentimentAnalysisState) -> Dict:
    scraped = []

    for url in state.search_results:
        try:
            html = requests.get(url, timeout=5).text
            soup = BeautifulSoup(html, "html.parser")
            text = " ".join(p.text for p in soup.find_all("p"))
            scraped.append(ScrapedArticle(url=url, content=text))
        except Exception:
            continue

    return {"scraped_articles": scraped}

def filter_articles(state: SentimentAnalysisState) -> Dict:
    coin = state.coin_name.lower()

    relevant = [
        art for art in state.scraped_articles
        if coin in art.content.lower()
    ]

    return {"filtered_articles": relevant}


def analyze_sentiment(state: SentimentAnalysisState) -> Dict:
    analyzed = []

    for art in state.filtered_articles:
        prompt = f"""
        You are a sentiment analysis model.

        Provide **only** a single sentiment score between -1 and 1
        for the following text. Do not output anything else.

        Text:
        {art.content[:6000]}
        """

        try:
            response = ollama_llm.invoke(prompt)
            score = float(str(response).strip())
        except Exception:
            score = 0.0

        analyzed.append(
            AnalyzedArticle(url=art.url, sentiment=score, content=art.content)
        )

    return {"analyzed_articles": analyzed}

def aggregate_results(state: SentimentAnalysisState) -> Dict:
    articles = state.analyzed_articles

    if not articles:
        final = FinalReport(
            coin_name=state.coin_name,
            days=state.days,
            top_articles=[],
            average_sentiment=0.0,
            sentiment_trend="unknown"
        )
        return {"final_report": final}

    sorted_articles = sorted(articles, key=lambda a: abs(a.sentiment), reverse=True)
    top3 = sorted_articles[:3]

    avg_sent = float(np.mean([a.sentiment for a in articles]))

    if len(articles) > 1:
        trend = "increasing" if articles[-1].sentiment > articles[0].sentiment else "decreasing"
    else:
        trend = "unknown"

    top3_articles_schema = [
        Article(
            title="N/A", 
            url=a.url,
            sentiment=a.sentiment
        )
        for a in top3
    ]

    final = FinalReport(
        coin_name=state.coin_name,
        days=state.days,
        top_articles=top3_articles_schema,
        average_sentiment=avg_sent,
        sentiment_trend=trend
    )

    return {"final_report": final}






