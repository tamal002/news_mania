"""Prompt builder for semantic news-article deduplication."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence


DEDUP_PROMPT_TEMPLATE = """\
You are the deduplication stage of a news aggregation pipeline. Select one
canonical article for each distinct underlying news event. The downstream
pipeline will summarize the selected articles, so return articles only; do
not return duplicate groups, explanations, confidence scores, or commentary.

## What counts as a duplicate

Treat articles as duplicates only when they are alternative coverage of the
same event or announcement. Require strong agreement on:

- the same subject or entities;
- the same event or claim;
- approximately the same time window; and
- compatible concrete details such as the action, location, product, version,
  funding amount, or people involved.

Apply these rules:

1. Exact or near-identical URLs are duplicates after ignoring URL fragments,
   tracking parameters, and harmless trailing-slash differences.
2. Syndicated, copied, or lightly rewritten versions of one report are
   duplicates even when their URLs, titles, or sources differ.
3. Articles about the same company, person, product, or topic are not
   duplicates unless the underlying event is the same.
4. A follow-up, correction, later milestone, later result, or separate release
   remains separate, even when it references the earlier story.
5. An opinion, analysis, tutorial, review, job post, or general background
   article is not automatically a duplicate of a news report.
6. Do not infer missing facts. When evidence is insufficient, keep both
   articles. False merges are worse than missed duplicates.
7. For each duplicate set, retain exactly one canonical article. Prefer the
   most authoritative or primary source, then the clearest and most complete
   report, then the earliest publication time, then the lowest stable `id`.
8. Preserve the selected article's `id` exactly as `article_id`. Never invent,
   alter, or omit an ID.

## Output contract

Return ONLY valid JSON. Do not use Markdown fences or add commentary.

The JSON must have exactly this shape, compatible with the
`DeduplicationResult` schema:

{{
  "articles": [
    {{
      "article_id": "the selected input article id",
      "title": "the selected input title",
      "url": "the selected input URL",
      "source": "the selected input source",
      "published_at": "the selected input timestamp or null"
    }}
  ]
}}

The `articles` array must contain exactly one item for every distinct event.
Every item must be copied from one input article. Preserve `title`, `url`,
`source`, and `published_at` exactly; do not summarize, normalize, or rewrite
them. Return an empty array when the input is empty.

## Examples

### Example 1: syndicated coverage — merge

Input:
[
  {{"id": "a1", "title": "Acme launches Orbit 2.0 with offline mode",
   "url": "https://news.example.com/orbit-2", "source": "rss",
   "published_at": "2026-10-01T09:00:00Z"}},
  {{"id": "a2", "title": "Acme's Orbit 2.0 adds offline support",
   "url": "https://social.example.com/posts/orbit-2", "source": "reddit",
   "published_at": "2026-10-01T10:00:00Z"}}
]

Output:
{{"articles": [
  {{"article_id": "a1",
   "title": "Acme launches Orbit 2.0 with offline mode",
   "url": "https://news.example.com/orbit-2",
   "source": "rss", "published_at": "2026-10-01T09:00:00Z"}}
]}}

### Example 2: same topic, different events — keep separate

Input:
[
  {{"id": "b1", "title": "Nova raises $40M Series B",
   "url": "https://example.com/nova-series-b", "source": "rss",
   "published_at": null}},
  {{"id": "b2", "title": "Nova releases its open-source database",
   "url": "https://example.com/nova-database", "source": "hn",
   "published_at": null}}
]

Output:
{{"articles": [
  {{"article_id": "b1", "title": "Nova raises $40M Series B",
   "url": "https://example.com/nova-series-b", "source": "rss",
   "published_at": null}},
  {{"article_id": "b2", "title": "Nova releases its open-source database",
   "url": "https://example.com/nova-database", "source": "hn",
   "published_at": null}}
]}}

### Example 3: follow-up update — keep separate

Input:
[
  {{"id": "c1", "title": "Regulator opens inquiry into Acme",
   "url": "https://example.com/acme-inquiry", "source": "rss",
   "published_at": null}},
  {{"id": "c2", "title": "Regulator fines Acme $10M after inquiry",
   "url": "https://example.com/acme-fine", "source": "rss",
   "published_at": null}}
]

Output:
{{"articles": [
  {{"article_id": "c1", "title": "Regulator opens inquiry into Acme",
   "url": "https://example.com/acme-inquiry", "source": "rss",
   "published_at": null}},
  {{"article_id": "c2", "title": "Regulator fines Acme $10M after inquiry",
   "url": "https://example.com/acme-fine", "source": "rss",
   "published_at": null}}
]}}

## Articles to classify

{articles_json}
"""


def build_dedup_prompt(articles: Sequence[Mapping[str, object]]) -> str:
    """Render the deduplication prompt with articles encoded as JSON."""

    return DEDUP_PROMPT_TEMPLATE.format(
        articles_json=json.dumps(
            list(articles),
            ensure_ascii=False,
            default=str,
            indent=2,
        )
    )


__all__ = ["DEDUP_PROMPT_TEMPLATE", "build_dedup_prompt"]
