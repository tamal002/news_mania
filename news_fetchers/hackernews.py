import requests
from dotenv import load_dotenv
from datetime import datetime, timezone

from state import Article

load_dotenv()


def fetch_news_id_from_hackernews():
    '''
    Fetches the IDs of the latest news items from Hacker News.
    '''
    url = "https://hacker-news.firebaseio.com/v0/newstories.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            return data[:20]
    except requests.RequestException as e:
        print(f"Error occurred while fetching news from Hacker News: {e}")
        return None


def fetch_news_using_hackernews_id() -> list[Article] | None:
    '''
    Fetches the details of news items from Hacker News using their IDs.
    '''
    news_ids = fetch_news_id_from_hackernews()
    if not news_ids:
        return []

    news_data: list[Article] = []
    count = 1
    for news_id in news_ids:
        url = f"https://hacker-news.firebaseio.com/v0/item/{news_id}.json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            if response.status_code == 200:
                data = response.json()
                if data is None:
                    continue

                article = Article(
                    id=count,
                    title=data.get("title", ""),
                    url=data.get("url", ""),
                    source="hn",
                    published_at=(datetime.fromtimestamp(data.get("time", 0), tz=timezone.utc) if data.get("time") else None)
                )
                news_data.append(article)
                count += 1
        except requests.RequestException as e:
            print(f"Error occurred while fetching news details for ID {news_id}: {e}")
            continue

    return news_data








