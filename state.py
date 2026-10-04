import operator
from typing import Annotated, TypedDict
from datetime import datetime
from pydantic import BaseModel, Field


class Article(TypedDict):
    id: int
    title: str
    url: str
    source: str                 # "hn" | "techcrunch_rss" | "github" | "reddit" | "tavily"
    published_at: datetime | None


class UniqueArticle(BaseModel):
    article_id: int = Field(description="integer id of the article in the NewsState.deduped_articles map")
    title: str = Field(description="title of the article")
    url: str = Field(description="URL of the article")
    source: str = Field(description="source of the article")
    published_at: datetime | None = Field(description="publication date of the article")


class DeduplicationResult(BaseModel):
    articles: list[UniqueArticle] = Field(
        description="One canonical article for each distinct underlying news event"
    )


class SummarizedArticle(TypedDict):
    title: str
    url: str
    source: str
    also_covered_by: list[str]
    summary: str


class NewsState(TypedDict):
    # --- fetch stage ---
    raw_articles: Annotated[list[Article], operator.add]   # reducer: parallel fetchers all append here


    deduped_articles: list[UniqueArticle]          # final unique set after merge — overwritten, not accumulated
    

    # --- summarize/email stage ---
    # summaries: list[SummarizedArticle]
    email_body: str

    # --- run metadata ---
    # run_timestamp: str
    errors: str