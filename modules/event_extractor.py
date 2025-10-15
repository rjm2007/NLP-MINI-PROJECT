import re
import spacy
from typing import List, Dict, Tuple
from .settings import (
    IGNORE_IF_CONTAINS, DROP_SENTENCE_IF_MATCHES, MIN_EVENT_LEN_CHARS,
    HEADLINE_MAX_LEN, HEADLINE_MIN_WORDS, PROXIMITY_WINDOW
)

nlp = spacy.load("en_core_web_sm")

def _keep_sentence(s: str) -> bool:
    """Filter out junk sentences."""
    low = s.lower()
    if any(bad in low for bad in IGNORE_IF_CONTAINS):
        return False
    for pattern in DROP_SENTENCE_IF_MATCHES:
        if re.fullmatch(pattern, s.strip(), flags=re.I):
            return False
    if len(s) < MIN_EVENT_LEN_CHARS:  # too small content
        return False
    return True

def _is_headline_like(s: str) -> bool:
    """Identify lines that look like headlines for event clustering."""
    if len(s) > HEADLINE_MAX_LEN:
        return False
    if len(s.split()) < HEADLINE_MIN_WORDS:
        return False
    if s.strip().endswith((".", ":", "-", "—", "…")):
        return False
    if s.count(".") > 1:
        return False
    # Check capitalization like titles
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", s)
    if not words:
        return False
    capitalized = sum(1 for w in words if w[0].isupper())
    return capitalized / len(words) > 0.5

def split_sentences(text: str) -> List[str]:
    doc = nlp(text)
    sentences = [s.text.strip() for s in doc.sents]
    return [s for s in sentences if _keep_sentence(s)]

def sentences_with_dates(sentences: List[str], date_mentions: List[Dict]) -> List[Tuple[str, object, int]]:
    hits = []
    for i, sent in enumerate(sentences):
        low = sent.lower()
        for m in date_mentions:
            if m["surface"].lower() in low:
                hits.append((m["surface"], m["normalized"], i))
    return hits

def _pair_headlines(sentences, hits):
    idx_to_dates = {}
    for surf, dt, idx in hits:
        idx_to_dates.setdefault(idx, []).append((surf, dt))
    new_hits = hits[:]
    for i, sent in enumerate(sentences):
        if _is_headline_like(sent) and i not in idx_to_dates:
            closest = sorted(hits, key=lambda h: abs(h[2] - i))
            if closest:
                new_hits.append((closest[0][0], closest[0][1], i))
    return new_hits

def cluster_events(sentences: List[str], hits, window=0):
    hits = _pair_headlines(sentences, hits)
    events = []
    seen = set()
    for surf, dt, i in hits:
        start = max(i - window, 0)
        end = min(i + window + 1, len(sentences))
        chunk = " ".join(sentences[start:end])
        key = (dt.date() if dt else None, chunk[:50])
        if key in seen:
            continue
        events.append({
            "date": dt,
            "text": chunk,
            "surface": surf,
            "anchor_sentence_index": i
        })
        seen.add(key)
    return events
