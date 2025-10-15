from datetime import datetime
from typing import List, Dict

def _sort_key(e):
    """
    Sort by full date first, then by year,
    undated events go last.
    """
    if e.get("date"):
        return (0, e["date"])
    if e.get("year"):
        return (1, datetime(e["year"], 1, 1))
    return (2, datetime.max)

def dedupe_events(events: List[Dict]):
    """Remove duplicate events by text + date/year."""
    seen = set()
    unique = []
    for e in events:
        key = (e.get("date") or e.get("year"), e["text"].strip().lower())
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique

def build_timeline(events: List[Dict]):
    """Return clean sorted timeline."""
    events = dedupe_events(events)
    return sorted(events, key=_sort_key)

def to_export_rows(events: List[Dict]):
    """Format export rows for JSON/CSV output."""
    formatted = []
    for e in events:
        formatted.append({
            "date": e["date"].strftime("%Y-%m-%d") if e.get("date") else None,
            "year": e.get("year"),
            "event": e["text"],
            "matched_phrase": e.get("surface")
        })
    return formatted
