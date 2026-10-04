from graph import get_graph
from state import NewsState


def main():

    try:
        graph = get_graph()
        initial_state = NewsState(
            raw_articles=[],
            deduped_articles=[],
            email_body="",
            errors=""
        )
        result = graph.invoke(initial_state)
        final_articles = result["deduped_articles"]
        print("Graph execution completed successfully.")
        for article in final_articles:
            print(f"Article ID: {article.article_id}\nTitle: {article.title}\nURL: {article.url}\nSource: {article.source}\nPublished At: {article.published_at}\n\n\n")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
