
from state import NewsState, Article, DeduplicationResult
from dotenv import load_dotenv
from news_fetchers.hackernews import fetch_news_using_hackernews_id
from llm import get_dedup_llm
from prompts.dedup_prompt import build_dedup_prompt


load_dotenv()

# hackernews_url_for_ids = "https://hacker-news.firebaseio.com/v0/newstories.json"
# hackernews_url_for_item = "https://hacker-news.firebaseio.com/v0/item/{}.json"



def fetch_news_from_hackernews_node(state: NewsState) -> dict:
    news_data: list[Article] | None = fetch_news_using_hackernews_id()
    return {"raw_articles": news_data} if news_data is not None else {"raw_articles": []}


def fetch_news_from_rss_node(state: NewsState) -> dict:
    pass


def fetch_news_from_github_node(state: NewsState) -> dict:
    pass


def fetch_news_from_reddit_node(state: NewsState) -> dict:
    pass


def deduplicate_news_node(state: NewsState) -> dict:
    dedup_llm = get_dedup_llm()
    prompt = build_dedup_prompt(state["raw_articles"])
    try:
        response: DeduplicationResult = dedup_llm.invoke(prompt)
        return {"deduped_articles": response.articles}
    except Exception as e:
        print(f"Error occurred during deduplication: {e}")
        return {"deduped_articles": []}
    


def summarize_news_node(state: NewsState) -> dict:
    pass


def generate_and_send_email_node(state: NewsState) -> dict:
    pass
