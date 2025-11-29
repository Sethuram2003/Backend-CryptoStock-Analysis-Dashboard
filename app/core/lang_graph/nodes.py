from app.core.lang_graph.schema import (
    SentimentAnalysisState,
    ScrapedArticle,
    AnalyzedArticle,
    FinalReport,
    Article,
)


from typing import Dict
import os
import requests
from bs4 import BeautifulSoup
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- NEW: Gemini / LangChain imports ---
from langchain_google_genai import ChatGoogleGenerativeAI

# Make sure your GOOGLE_API_KEY is set in the environment
os.environ["GOOGLE_API_KEY"] = "AIzaSyAZMkwl6rUmaSB3nx8u-wSqI9VWDgOpBYA"

# Initialize Gemini LLM (drop-in replacement for ollama_llm)
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",  # or "gemini-1.5-flash"
    temperature=0,
)


def search_news(state: SentimentAnalysisState) -> Dict:
    query = f"{state.coin_name} cryptocurrency news last {state.days} days"
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&apiKey=9b5455fab616452d95eebe6181d08a05"
    )

    try:
        response = requests.get(url).json()
        links = [a["url"] for a in response.get("articles", [])]
    except Exception:
        links = []

    return {"search_results": links}


def scrape_single_article(url: str, headers):
    """Scrape & process a single article (runs in parallel)."""
    try:
        res = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(res.text, "html.parser")

        text = " ".join([p.get_text(strip=True) for p in soup.find_all("p")])
        if len(text) < 100:
            return None

        title = None

        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            title = og["content"]

        if not title:
            meta_title = soup.find("meta", attrs={"name": "title"})
            if meta_title and meta_title.get("content"):
                title = meta_title["content"]

        if not title and soup.title:
            title = soup.title.text.strip()

        if not title or title == "Unknown Title":
            # Use Gemini to generate a title
            title_prompt = f"""
            You are an expert news headline generator.

            Read the following article content and generate a clear,
            concise, professional news article title (max 12 words).

            Content:
            {text[:2000]}

            Return ONLY the title, no quotation marks, no commentary.
            """
            try:
                msg = gemini_llm.invoke(title_prompt)
                # ChatGoogleGenerativeAI returns an AIMessage with `.content`
                title = msg.content.strip()
            except Exception:
                title = "Generated Title"

        return ScrapedArticle(url=url, content=text, title=title)

    except Exception:
        return None


def scrape_articles(state: SentimentAnalysisState):
    headers = {"User-Agent": "Mozilla/5.0"}

    scraped = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(scrape_single_article, url, headers): url
            for url in state.search_results
        }

        for future in as_completed(futures):
            result = future.result()
            if result:
                scraped.append(result)

    return {"scraped_articles": scraped}


def filter_articles(state: SentimentAnalysisState) -> Dict:
    coin = state.coin_name.lower()

    relevant = [
        art
        for art in state.scraped_articles
        if coin in art.content.lower()
    ]

    return {"filtered_articles": relevant}


def analyze_single_article(art):
    """LLM sentiment analysis for a single article (runs in parallel)."""
    prompt = f"""
    You are a sentiment analysis model.

    Provide ONLY a single sentiment score between -1 and 1
    for the following text.

    Text:
    {art.content[:6000]}
    """
    try:
        msg = gemini_llm.invoke(prompt)
        score_text = str(msg.content).strip()
        score = float(score_text)
    except Exception:
        score = 0.0

    return AnalyzedArticle(
        url=art.url,
        sentiment=score,
        content=art.content,
        title=art.title,
    )


def analyze_sentiment(state: SentimentAnalysisState) -> Dict:
    analyzed = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(analyze_single_article, art): art.url
            for art in state.filtered_articles
        }

        for future in as_completed(futures):
            result = future.result()
            analyzed.append(result)

    return {"analyzed_articles": analyzed}


def aggregate_results(state: SentimentAnalysisState) -> Dict:
    articles = state.analyzed_articles

    if not articles:
        final = FinalReport(
            coin_name=state.coin_name,
            days=state.days,
            top_articles=[],
            average_sentiment=0.0,
            sentiment_trend="unknown",
        )
        return {"final_report": final}

    sorted_articles = sorted(articles, key=lambda a: abs(a.sentiment), reverse=True)
    top3 = sorted_articles[:3]

    avg_sent = float(np.mean([a.sentiment for a in articles]))

    if len(articles) > 1:
        trend = (
            "increasing"
            if articles[-1].sentiment > articles[0].sentiment
            else "decreasing"
        )
    else:
        trend = "unknown"

    top3_articles_schema = [
        Article(
            title=a.title,
            url=a.url,
            sentiment=a.sentiment,
        )
        for a in top3
    ]

    final = FinalReport(
        coin_name=state.coin_name,
        days=state.days,
        top_articles=top3_articles_schema,
        average_sentiment=avg_sent,
        sentiment_trend=trend,
    )

    return {"final_report": final}
