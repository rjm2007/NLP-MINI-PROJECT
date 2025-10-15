import re
from datetime import datetime, timedelta
from dateutil import parser as dateparser
from dateutil.relativedelta import relativedelta
import spacy
from .date_patterns import DATE_MASTER_REGEX, RELATIVE_PATTERNS, RANGE_PATTERNS
from .settings import REF_YEAR_TOLERANCE_FUTURE

nlp = spacy.load("en_core_web_sm")

# Ignore useless date-like junk
JUNK_PATTERNS = [
    r"^\d+\s+\d+\s+\d+$",
    r"^\d+\s*years?$",
    r"^\d+\s*days?$",
]

# Capture YEAR separately
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

def find_years(text: str, ref_date: datetime):
    years = []
    for m in YEAR_RE.findall(text or ""):
        y = int(m)
        if 1900 <= y <= (ref_date.year + REF_YEAR_TOLERANCE_FUTURE):
            if y not in years:
                years.append(y)
    return years

def normalize_absolute_date(text: str, dayfirst=True):
    # Skip pure year-only here (years handled separately)
    if re.fullmatch(r"(19|20)\d{2}", text.strip()):
        return None
    try:
        return dateparser.parse(text.strip(), dayfirst=dayfirst, fuzzy=True)
    except Exception:
        return None

def normalize_relative_phrase(text: str, ref_date: datetime):
    t = text.lower()
    for phrase, (unit, value) in RELATIVE_PATTERNS:
        if phrase in t:
            if unit == "days":    return ref_date + timedelta(days=value)
            if unit == "weeks":   return ref_date + timedelta(weeks=value)
            if unit == "months":  return ref_date + relativedelta(months=value)
            if unit == "years":   return ref_date + relativedelta(years=value)
    return None

def extract_date_mentions(text: str, ref_date: datetime):
    mentions = []

    # ----- Extract Date Ranges -----
    for rx in RANGE_PATTERNS:
        for m in rx.finditer(text):
            parts = m.groups()
            if len(parts) == 5:  # month1 day1 to month2 day2, year
                m1, d1, m2, d2, y = parts
                year = int(y) if y else ref_date.year
            else:
                continue
            try:
                dt1 = dateparser.parse(f"{d1} {m1} {year}")
                dt2 = dateparser.parse(f"{d2} {m2} {year}")
                mentions.append({"surface": m.group(0), "normalized": dt1})
                mentions.append({"surface": m.group(0), "normalized": dt2})
            except:
                pass

    # ----- Extract direct date formats -----
    for m in DATE_MASTER_REGEX.finditer(text):
        date_str = next(g for g in m.groups() if g)
        if re.fullmatch(r"(19|20)\d{2}", date_str): # skip plain year
            continue
        dt = normalize_absolute_date(date_str)
        if dt:
            mentions.append({"surface": date_str, "normalized": dt})

    # ----- Extract via SpaCy NER -----
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "DATE":
            s = ent.text.strip()
            if re.fullmatch(r"(19|20)\d{2}", s):  # skip plain year
                continue
            dt = normalize_absolute_date(s)
            if dt:
                mentions.append({"surface": s, "normalized": dt})

    # Dedupe results
    final = []
    seen = set()
    for m in mentions:
        key = (m["surface"], m["normalized"].date())
        if key not in seen:
            seen.add(key)
            final.append(m)
    return final
