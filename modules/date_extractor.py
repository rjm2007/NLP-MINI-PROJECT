import re
from datetime import datetime, timedelta
from dateutil import parser as dateparser
from dateutil.relativedelta import relativedelta
import spacy

from .date_patterns import DATE_MASTER_REGEX, RELATIVE_PATTERNS, RANGE_PATTERNS
from .settings import REF_YEAR_TOLERANCE_FUTURE

nlp = spacy.load("en_core_web_sm")

JUNK_PATTERNS = [
    r"^\d+\s+\d+\s+\d+$",      # "1 2 3"
    r"^\d+\s*years?$",         # "11 years"
    r"^\d+\s*days?$",          # "44 days"
]

MONTH_TO_NUM = {
    "jan":1,"january":1,"feb":2,"february":2,"mar":3,"march":3,"apr":4,"april":4,
    "may":5,"jun":6,"june":6,"jul":7,"july":7,"aug":8,"august":8,"sep":9,"september":9,
    "oct":10,"october":10,"nov":11,"november":11,"dec":12,"december":12
}

def _matches_any(pats, text):
    t = text.strip()
    for p in pats:
        if re.fullmatch(p, t, flags=re.I):
            return True
    return False

def _quarter_start(ref: datetime, shift: int) -> datetime:
    q = (ref.month - 1) // 3 + 1
    target_q = q + shift
    target_year = ref.year + (target_q - 1) // 4
    target_q = ((target_q - 1) % 4) + 1
    month_start = 3 * (target_q - 1) + 1
    return datetime(target_year, month_start, 1)

def _normalize_quarter(qstr: str):
    m = re.match(r"Q([1-4])[- ]?(\d{4})", qstr, flags=re.I)
    if not m: return None
    q = int(m.group(1)); year = int(m.group(2))
    month = 3 * (q - 1) + 1
    return datetime(year, month, 1)

def normalize_absolute_date(text: str, dayfirst=True):
    text = text.strip().strip(",")
    # ❌ Skip pure year-only (user requested)
    if re.fullmatch(r"(19|20)\d{2}", text):
        return None
    q = _normalize_quarter(text)
    if q: return q
    try:
        return dateparser.parse(text, dayfirst=dayfirst, fuzzy=True)
    except Exception:
        return None

def normalize_relative_phrase(phrase: str, ref_date: datetime):
    phrase = phrase.lower().strip()
    for key, (rtype, val) in RELATIVE_PATTERNS:
        if key in phrase:
            if rtype == "days":    return ref_date + timedelta(days=val)
            if rtype == "weeks":   return ref_date + timedelta(weeks=val)
            if rtype == "months":  return ref_date + relativedelta(months=val)
            if rtype == "years":   return ref_date + relativedelta(years=val)
            if rtype == "quarter": return _quarter_start(ref_date, val)
            if rtype == "this":    return ref_date
    return None

def is_noisy_date(span_text: str):
    noisy = {
        "monday","tuesday","wednesday","thursday","friday","saturday","sunday",
        "spring","summer","autumn","fall","winter","weekend","fortnight"
    }
    t = span_text.lower().strip()
    if t in noisy:
        return True
    if re.search(r"\b(over|for)\s+\d+\s+(days?|weeks?)\b", t):
        return True
    return False

def _year_sane(dt: datetime, ref: datetime) -> bool:
    if not dt: return False
    if dt.year < 1900: return False
    if dt.year > ref.year + REF_YEAR_TOLERANCE_FUTURE: return False
    return True

def _month_to_num(m: str) -> int:
    return MONTH_TO_NUM[m.lower()]

def _expand_ranges(text: str, ref_date: datetime):
    out = []
    for rx in RANGE_PATTERNS:
        for m in rx.finditer(text):
            groups = [g for g in m.groups()]
            # Two pattern shapes; disambiguate by number of groups
            if len(groups) == 5:  # month day to month day , year?
                m1, d1, m2, d2, y = groups
                year = int(y) if y else ref_date.year
                try:
                    dt1 = datetime(year, _month_to_num(m1), int(d1))
                    dt2 = datetime(year, _month_to_num(m2), int(d2))
                except Exception:
                    continue
            else:  # same-month range: month d1–d2 , year?
                m1, d1, d2, y = groups
                year = int(y) if y else ref_date.year
                try:
                    dt1 = datetime(year, _month_to_num(m1), int(d1))
                    dt2 = datetime(year, _month_to_num(m1), int(d2))
                except Exception:
                    continue
            if _year_sane(dt1, ref_date) and _year_sane(dt2, ref_date):
                surface = m.group(0)
                out.append({"surface": surface+" (start)", "normalized": dt1, "kind":"range"})
                out.append({"surface": surface+" (end)",   "normalized": dt2, "kind":"range"})
    return out

def extract_date_mentions(text: str, ref_date: datetime):
    mentions = []

    # 1) Expand explicit ranges to endpoints
    mentions.extend(_expand_ranges(text, ref_date))

    # 2) Regex absolute dates
    for m in DATE_MASTER_REGEX.finditer(text):
        surface = next(g for g in m.groups() if g)
        # Skip year-only and noise/junk
        if re.fullmatch(r"(19|20)\d{2}", surface):
            continue
        if is_noisy_date(surface) or _matches_any(JUNK_PATTERNS, surface):
            continue
        norm = normalize_absolute_date(surface)
        if norm and not _year_sane(norm, ref_date):
            continue
        if norm:
            mentions.append({"surface": surface, "normalized": norm, "kind": "absolute"})

    # 3) spaCy NER fallback (absolute + relative)
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ != "DATE": 
            continue
        s = ent.text.strip()
        if re.fullmatch(r"(19|20)\d{2}", s):  # skip year-only
            continue
        if is_noisy_date(s) or _matches_any(JUNK_PATTERNS, s):
            continue
        norm = normalize_absolute_date(s)
        kind = "ner"
        if (not norm):
            norm = normalize_relative_phrase(s, ref_date)
            if norm:
                kind = "relative"
        if norm and not _year_sane(norm, ref_date):
            continue
        if norm:
            mentions.append({"surface": s, "normalized": norm, "kind": kind})

    # Deduplicate by (surface, normalized)
    dedup = {}
    for m in mentions:
        key = (m["surface"].lower(), m["normalized"].date())
        dedup[key] = m
    return list(dedup.values())
