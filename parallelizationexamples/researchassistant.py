from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from scholarly import scholarly
import wikipediaapi
import requests

from util import llm, newsapi_key



# Graph state
class State(TypedDict):
    topic: str
    scholar_info: str
    wikipedia_info: str
    news_info: str
    combined_output: str

# Nodes
def fetch_google_scholar(state: State):
    """Fetches research papers, summaries, and links from Google Scholar"""
    
    search_results = scholarly.search_pubs(state["topic"])
    papers = []
    
    for result in search_results:
        title = result.get("bib", {}).get("title", "No Title")
        author = result.get("bib", {}).get("author", "Unknown")
        summary = result.get("bib", {}).get("abstract", "No summary available")  # Extract abstract
        link = result.get("pub_url", "No link available")  # Get the link to the full paper
        
        papers.append(f"Title: {title}\nAuthor: {author}\nSummary: {summary}\nLink: {link}\n")
        
        if len(papers) >= 3:  # Limit to 3 papers
            break
    
    return {"scholar_info": "\n\n".join(papers)}

def fetch_wikipedia(state: State):
    """Fetches summary from Wikipedia with a proper user agent"""
    
    USER_AGENT = "MyResearchAgent/1.0 (atulmailing@gmail.com)"  # Customize this
    
    # Initialize Wikipedia with user_agent in the constructor
    wiki = wikipediaapi.Wikipedia(
        user_agent=USER_AGENT,
        language='en'
    )
    
    page = wiki.page(state["topic"])
    
    if not page.exists():
        return {"wikipedia_info": "No Wikipedia page found for this topic."}
    
    summary = page.summary[:500]  # First 500 characters
    return {"wikipedia_info": summary}

def fetch_news(state: State):
    """Fetches recent news articles with their URLs"""
    api_key = newsapi_key
    url = f"https://newsapi.org/v2/everything?q={state['topic']}&apiKey={api_key}"
    response = requests.get(url).json()
    articles = response.get("articles", [])
    
    if not articles:
        return {"news_info": "No news available."}
    
    # Create formatted strings with headlines and URLs
    news_items = []
    for article in articles[:3]:
        headline = article["title"]
        article_url = article["url"]
        news_items.append(f"{headline}\nURL: {article_url}\n")
    
    return {"news_info": "\n".join(news_items)}

def aggregator(state: State):
    """Combines all the sources into a single research report"""
    combined = f"Research on {state['topic']}:\n\n"
    combined += f"🔍 **Google Scholar Papers:**\n{state['scholar_info']}\n\n"
    combined += f"📖 **Wikipedia Summary:**\n{state['wikipedia_info']}\n\n"
    combined += f"📰 **Latest News:**\n{state['news_info']}"
    return {"combined_output": combined}

# Build workflow
parallel_builder = StateGraph(State)

# Add nodes
parallel_builder.add_node("fetch_google_scholar", fetch_google_scholar)
parallel_builder.add_node("fetch_wikipedia", fetch_wikipedia)
parallel_builder.add_node("fetch_news", fetch_news)
parallel_builder.add_node("aggregator", aggregator)

# Add edges to connect nodes
parallel_builder.add_edge(START, "fetch_google_scholar")
parallel_builder.add_edge(START, "fetch_wikipedia")
parallel_builder.add_edge(START, "fetch_news")
parallel_builder.add_edge("fetch_google_scholar", "aggregator")
parallel_builder.add_edge("fetch_wikipedia", "aggregator")
parallel_builder.add_edge("fetch_news", "aggregator")
parallel_builder.add_edge("aggregator", END)
parallel_workflow = parallel_builder.compile()

# Show workflow
display(Image(parallel_workflow.get_graph().draw_mermaid_png()))

# Invoke
state = parallel_workflow.invoke({"topic": "Sonar in navigation"})
print(state["combined_output"])
