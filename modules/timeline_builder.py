from datetime import datetime
from typing import List, Dict

def _event_key(e):
    if e["date"] is None:
        return (datetime.max, e["text"][:60].lower())
    return (e["date"], e["text"][:60].lower())

def dedupe_events(events: List[Dict]):
    seen = set()
    out = []
    for e in events:
        key = (e["date"].date() if e["date"] else None, e["text"].lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out

def build_timeline(events: List[Dict]):
    events = dedupe_events(events)
    events.sort(key=_event_key)
    return events

def to_export_rows(events: List[Dict]):
    rows = []
    for e in events:
        rows.append({
            "date": (e["date"].strftime("%Y-%m-%d") if e["date"] else None),
            "event": e["text"],
            "matched_phrase": e.get("surface"),
        })
    return rows
