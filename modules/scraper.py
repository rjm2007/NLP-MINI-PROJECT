import re
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

# Site sections we never want
NOISE_SELECTORS = (
    "script, style, nav, noscript, header, footer, figure, aside, form, iframe, "
    ".share, .social, .newsletter, .subscribe, .ad, [aria-label='advertisement'], "
    ".storyTags, .topnav, .breadcrumb, .liveblog, .recommended-stories, .story__tags"
)

# Textual junk common on Indian news sites
SITE_TEXT_NOISE = [
    r"(?is)\b(Abc Small Abc Medium Abc Large)\b.*?$",
    r"(?is)\b(IST Rate Story|Follow us|Share|Comment)\b.*?$",
    r"(?is)\b(You Might Also Like|Recommended|Read More|Subscribe|ETPrime|e[- ]?Paper)\b.*?$",
    r"(?is)\b(Benchmarks|Nifty|Sensex)\b.*?$",
]

MAIN_SELECTORS = [
    "article",
    "div[itemprop='articleBody']",
    "section[name='articleBody']",
    "div#content",
    "div.post-content",
    "div.entry-content",
    "main",
    "div.mw-parser-output",
]

def _clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s

def _strip_site_text_noise(text: str) -> str:
    for pat in SITE_TEXT_NOISE:
        text = re.sub(pat, "", text)
    # remove repeated spaces again
    return _clean_text(text)

def _extract_main_text(soup: BeautifulSoup) -> str:
    candidates = [soup.select_one(sel) for sel in MAIN_SELECTORS]
    candidates = [c for c in candidates if c] or [soup.body or soup]

    best_text, best_len = "", 0
    for node in candidates:
        # robust “clone”: reparse the node HTML into a mini-soup
        node_copy = BeautifulSoup(str(node), "lxml")
        for bad in node_copy.select(NOISE_SELECTORS):
            bad.decompose()
        text = node_copy.get_text(separator=" ", strip=True)
        text = _strip_site_text_noise(text)
        if len(text) > best_len:
            best_text, best_len = text, len(text)
    return best_text

def _extract_published_dt(soup: BeautifulSoup):
    for tag, attrs in [
        ("meta", {"property": "article:published_time"}),
        ("meta", {"property": "og:updated_time"}),
        ("meta", {"name": "pubdate"}),
        ("meta", {"name": "publish-date"}),
        ("meta", {"name": "date"}),
        ("meta", {"itemprop": "datePublished"}),
        ("time", {"datetime": True}),
    ]:
        el = soup.find(tag, attrs=attrs)
        if el:
            dt = el.get("content") or el.get("datetime") or el.get("value") or el.text
            if dt:
                try:
                    return dateparser.parse(dt)
                except Exception:
                    pass
    return None

def fetch_article(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (TimelineExtractor/1.0)"}
    resp = requests.get(url, headers=headers, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    text = _extract_main_text(soup)
    published_dt = _extract_published_dt(soup)
    return {
        "text": text,
        "published_at": published_dt,
        "title": (soup.title.string.strip() if soup.title and soup.title.string else ""),
        "url": url,
    }
