import re
import json
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from urllib.parse import urlparse

# Clean junk HTML sections
NOISE_SELECTORS = (
    "script, style, nav, noscript, header, footer, figure, aside, form, iframe,"
    ".share, .social, .newsletter, .subscribe, .ad, [aria-label='advertisement'],"
    ".storyTags, .topnav, .breadcrumb, .liveblog, .next-article, .pagination, .paywall"
)

def _clean_text(text):
    return re.sub(r"\s+", " ", text or "").strip()

def _extract_json_ld(soup):
    """Extract clean text + title from TOI JSON-LD if available."""
    blocks = soup.find_all("script", {"type": "application/ld+json"})
    article_body = None
    title = None
    publish_date = None

    for b in blocks:
        try:
            data = json.loads(b.string.strip())
            if isinstance(data, dict) and data.get("@type") == "NewsArticle":
                article_body = data.get("articleBody")
                title = data.get("headline")
                publish_date = data.get("datePublished")
                break
        except:
            continue

    return title, article_body, publish_date

def _fallback_text(soup):
    """Fallback if JSON-LD is not available."""
    for selector in ["article", "div[itemprop='articleBody']", ".Normal"]:
        tag = soup.select_one(selector)
        if tag:
            return tag.get_text(separator=" ")
    return ""

def fetch_article(url):
    """Main article fetcher."""
    headers = {"User-Agent": "Mozilla/5.0 (TimelineExtractor/4.3)"}
    res = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(res.text, "lxml")

    domain = urlparse(url).netloc.lower()
    is_toi = "timesofindia" in domain

    # Use JSON-LD for TOI (clean source)
    if is_toi:
        title, body, date_published = _extract_json_ld(soup)
        if not body:
            body = _fallback_text(soup)

        publish_date = None
        if date_published:
            try:
                publish_date = dateparser.parse(date_published)
            except:
                pass

        return {
            "title": title or soup.title.string.strip(),
            "text": _clean_text(body),
            "published_at": publish_date,
            "url": url
        }

    # If not TOI, fallback parsing (generic mode)
    body = _fallback_text(soup)
    return {
        "title": soup.title.string.strip() if soup.title else url,
        "text": _clean_text(body),
        "published_at": None,
        "url": url
    }
