import re
import spacy
from typing import List, Dict, Tuple
from .settings import (
    IGNORE_IF_CONTAINS, DROP_SENTENCE_IF_MATCHES, MIN_EVENT_LEN_CHARS,
    HEADLINE_MAX_LEN, HEADLINE_MIN_WORDS, PROXIMITY_WINDOW
)

nlp = spacy.load("en_core_web_sm")

def _keep_sentence(s: str) -> bool:
    low = s.lower()
    if any(tok in low for tok in IGNORE_IF_CONTAINS):
        return False
    for pat in DROP_SENTENCE_IF_MATCHES:
        if re.fullmatch(pat, s.strip(), flags=re.I):
            return False
    if len(s.strip()) < MIN_EVENT_LEN_CHARS:
        return False
    if not re.search(r"[A-Za-z]", s):
        return False
    # Drop generic “year recap” intros
    if re.search(r"\b20\d{2}\b.*\byear\b", low):
        return False
    return True

def _is_headline_like(s: str) -> bool:
    # short, few words, mostly title case or all caps, minimal punctuation
    if len(s) > HEADLINE_MAX_LEN: return False
    if len(s.split()) < HEADLINE_MIN_WORDS: return False
    if s.strip().endswith((".", ":", "—", "-", "…")): return False  # often intros, not headers
    # Heuristics: <=1 comma and <=1 period
    if s.count(",") > 1 or s.count(".") > 0:
        return False
    # TitleCase or ALL CAPS words ratio
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", s)]
    if not words: return False
    titleish = sum(1 for w in words if (w[0].isupper() and w[1:].islower()) or w.isupper())
    return (titleish / max(1, len(words))) >= 0.6

def split_sentences(text: str):
    sents = [s.text.strip() for s in nlp(text).sents if s.text.strip()]
    sents = [s for s in sents if _keep_sentence(s)]
    return sents

def sentences_with_dates(sentences: List[str], date_mentions: List[Dict]):
    """Return (surface, normalized_dt, sent_idx) where the sentence contains the surface."""
    hits = []
    for i, sent in enumerate(sentences):
        low = sent.lower()
        for m in date_mentions:
            if m["surface"].lower() in low:
                hits.append((m["surface"], m["normalized"], i))
    return hits

def _pair_headlines_with_nearby_dates(sentences: List[str],
                                      hits: List[Tuple[str, object, int]],
                                      window: int) -> List[Tuple[str, object, int]]:
    """If a headline-like sentence lacks a date, pair it with the closest nearby dated sentence."""
    # Build map: sentence idx -> list of (surface, dt) that appear in that sentence
    idx_to_dates = {}
    for surf, dt, idx in hits:
        idx_to_dates.setdefault(idx, []).append((surf, dt))

    augmented = hits[:]
    for i, s in enumerate(sentences):
        if not _is_headline_like(s):
            continue
        # If this headline already has a date, skip
        if i in idx_to_dates:
            continue
        # Search nearby sentences for any date
        best = None
        for j in range(max(0, i - PROXIMITY_WINDOW), min(len(sentences), i + PROXIMITY_WINDOW + 1)):
            if j in idx_to_dates:
                # pick the closest j
                for (surf, dt) in idx_to_dates[j]:
                    if best is None or abs(j - i) < best[0]:
                        best = (abs(j - i), surf, dt)
        if best:
            _, surf, dt = best
            augmented.append((surf, dt, i))
    return augmented

def cluster_events(sentences: List[str],
                   hits: List[Tuple[str, object, int]],
                   window: int = 0):
    """Create event entries as text blocks around anchor sentence."""
    # headline pairing first
    hits = _pair_headlines_with_nearby_dates(sentences, hits, window=max(PROXIMITY_WINDOW, window))

    events = []
    used = set()
    for surface, norm_dt, idx in hits:
        start = max(0, idx - window)
        end = min(len(sentences), idx + window + 1)
        key = (start, end, norm_dt.date() if norm_dt else None)
        if key in used:
            continue
        used.add(key)
        block = " ".join(sentences[j] for j in range(start, end)).strip()
        events.append({
            "date": norm_dt, "text": block, "surface": surface, "anchor_sentence_index": idx,
        })
    return events
