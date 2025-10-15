import re
from .settings import TRIM_AFTER_TOKENS, MAX_EVENT_LEN_CHARS

def _trim_after_tokens(text: str) -> str:
    for t in TRIM_AFTER_TOKENS:
        cut = text.find(t)
        if cut != -1:
            text = text[:cut]
    return text

def _keep_main_clause(text: str) -> str:
    # split by typical clause joiners to keep the core
    parts = re.split(r"\s+(?:which|that|as|while|where|when|but|and then)\b", text, maxsplit=1, flags=re.I)
    return parts[0].strip()

def _compact_spaces(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text

def summarize_event(raw: str) -> str:
    if not raw: 
        return raw
    t = raw.strip()
    t = _trim_after_tokens(t)
    t = _keep_main_clause(t)
    # remove parentheses blocks that are usually side-notes
    t = re.sub(r"\([^)]{0,120}\)", "", t).strip()
    # drop site-specific tails like “(Catch all the Business News...)”
    t = re.sub(r"(Catch all.*|Subscribe to.*|Read More.*)$", "", t, flags=re.I).strip()
    # compress
    t = _compact_spaces(t)
    # trim lengthy lines softly at sentence end or hard-cut
    if len(t) > MAX_EVENT_LEN_CHARS:
        m = re.match(r"(.{60,250}?[\.\!\?])\s", t)
        if m:
            t = m.group(1).strip()
        else:
            t = t[:MAX_EVENT_LEN_CHARS].rstrip() + "…"
    return t
