import re
from .settings import TRIM_AFTER_TOKENS, MAX_EVENT_LEN_CHARS

def _trim_noise(text: str) -> str:
    """Remove junk after ads or noise markers"""
    for token in TRIM_AFTER_TOKENS:
        if token in text:
            text = text.split(token)[0]
    return text

def summarize_event(text: str) -> str:
    """Clean and shorten event text for timeline output"""
    if not text:
        return ""

    # Remove brackets content
    text = re.sub(r"\([^)]*\)", "", text)

    # Remove long descriptions
    text = _trim_noise(text)

    # Keep main part of sentence
    text = re.split(r"(?<=\.)\s+| but | however ", text)[0]

    # Remove duplicate spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Too long? Truncate
    if len(text) > MAX_EVENT_LEN_CHARS:
        text = text[:MAX_EVENT_LEN_CHARS].rsplit(" ", 1)[0] + "..."

    return text.strip()
