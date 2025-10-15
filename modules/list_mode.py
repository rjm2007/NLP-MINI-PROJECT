import re
from datetime import datetime
from typing import List, Dict, Optional
from .event_summarizer import summarize_event
from .date_extractor import extract_date_mentions, find_years

# Detect numbered or bullet-point list articles
ITEM_SPLIT_RE = re.compile(
    r"(?:^\s*(?:\d{1,2}[\).:]|[-–•])\s+)|(?:\n\s*(?:\d{1,2}[\).:]|[-–•])\s+)",
    flags=re.M
)

def split_list_items(text: str) -> List[str]:
    """Split article body into bullet point items if it is a list article."""
    if not text:
        return []
    parts = ITEM_SPLIT_RE.split(text)
    items = [p.strip() for p in parts if p.strip() and len(p.strip()) > 25]
    return items

def build_events_from_items(items: List[str], ref_date: datetime) -> List[Dict]:
    """Convert list items into timeline events (supports year-based events)."""
    events = []
    for item in items:
        # Extract date or year
        mentions = extract_date_mentions(item, ref_date)
        year_candidates = find_years(item, ref_date)
        event_date = mentions[0]["normalized"] if mentions else None
        event_year = year_candidates[0] if year_candidates else None

        # Clean sentence
        summary = summarize_event(item)

        events.append({
            "date": event_date,
            "year": event_year,
            "text": summary,
            "surface": mentions[0]["surface"] if mentions else str(event_year) if event_year else None,
            "anchor_sentence_index": -1
        })
    return events
