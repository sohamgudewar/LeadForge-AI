import os
from urllib.parse import urlparse

import httpx

from models.outreach import ResearchSource

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
SEARCH_TIMEOUT_SECONDS = 12
MAX_RESULTS = 5


def _is_public_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        hostname = (parsed.hostname or "").lower()
        return (
            parsed.scheme in {"http", "https"}
            and bool(hostname)
            and hostname not in {"localhost", "127.0.0.1", "::1"}
            and not hostname.endswith(".local")
        )
    except ValueError:
        return False


def search_company(company: str) -> list[ResearchSource]:
    """Return current public evidence, or an empty list when search is unconfigured."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return []

    try:
        response = httpx.post(
            TAVILY_SEARCH_URL,
            json={
                "api_key": api_key,
                "query": f'"{company}" company products recent news',
                "search_depth": "advanced",
                "max_results": MAX_RESULTS,
                "include_answer": False,
                "include_raw_content": False,
            },
            timeout=SEARCH_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
    except (httpx.HTTPError, ValueError, TypeError):
        return []

    sources = []
    for item in results:
        url = str(item.get("url", ""))
        if not _is_public_http_url(url):
            continue
        source_id = f"S{len(sources) + 1}"
        sources.append(
            ResearchSource(
                source_id=source_id,
                title=str(item.get("title") or url)[:300],
                url=url,
                snippet=str(item.get("content") or "")[:1000],
            )
        )
        if len(sources) == MAX_RESULTS:
            break
    return sources
