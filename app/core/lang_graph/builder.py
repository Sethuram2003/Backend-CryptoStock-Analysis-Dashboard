from langgraph.graph import StateGraph, END

from app.core.lang_graph.schema import SentimentAnalysisState
from app.core.lang_graph.nodes import search_news, scrape_articles, filter_articles, analyze_sentiment, aggregate_results

def build_graph():
    workflow = StateGraph(SentimentAnalysisState)

    workflow.add_node("search", search_news)
    workflow.add_node("scrape", scrape_articles)
    workflow.add_node("filter", filter_articles)
    workflow.add_node("sentiment", analyze_sentiment)
    workflow.add_node("aggregate", aggregate_results)

    workflow.set_entry_point("search")

    workflow.add_edge("search", "scrape")
    workflow.add_edge("scrape", "filter")
    workflow.add_edge("filter", "sentiment")
    workflow.add_edge("sentiment", "aggregate")
    workflow.add_edge("aggregate", END)

    compiled_graph = workflow.compile()
    
    graph = compiled_graph.get_graph()
    
    try:
        png_bytes = graph.draw_mermaid_png()
        with open("app/core/lang_graph/workflow_diagram.png", "wb") as f:
            f.write(png_bytes)
        print("Mermaid diagram saved as workflow_diagram.png")
    except Exception as e:
        print(f"Could not generate Mermaid PNG: {e}")

    return compiled_graph


if __name__ == "__main__":
    agent = build_graph()
    response = agent.invoke({
                    "coin_name": "Bitcoin",
                    "days": 7
                })
    
    print(response)

