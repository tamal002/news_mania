from langgraph.graph import StateGraph, START, END
from state import NewsState
from nodes import fetch_news_from_hackernews_node, deduplicate_news_node, generate_email_body_node, send_email_node



def _build_graph():
    builder = StateGraph(NewsState)

    # adding nodes to the graph
    builder.add_node("fetch_news_from_hackernews_node", fetch_news_from_hackernews_node)
    builder.add_node("deduplicate_news_node", deduplicate_news_node)
    builder.add_node("generate_email_body_node", generate_email_body_node)
    builder.add_node("send_email_node", send_email_node)

    # defining the flow of the graph
    builder.add_edge(START, "fetch_news_from_hackernews_node")
    builder.add_edge("fetch_news_from_hackernews_node", "deduplicate_news_node")
    builder.add_edge("deduplicate_news_node", "generate_email_body_node")
    builder.add_edge("generate_email_body_node", "send_email_node")
    builder.add_edge("send_email_node", END)

    return builder.compile()


def get_graph():
    return _build_graph()