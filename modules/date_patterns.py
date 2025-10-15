import re

# Month names pattern
MONTHS = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|" \
         r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"

# Absolute date regex patterns
DATE_REGEXPS = [
    # March 21, 2024 OR Mar 21 2024
    rf"\b{MONTHS}\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,)?\s+\d{{4}}\b",
    # 21 March 2024
    rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+{MONTHS}\s+\d{{4}}\b",
    # YYYY-MM-DD or YYYY/MM/DD
    r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",
    # Month Year e.g. March 2024
    rf"\b{MONTHS}\s+\d{{4}}\b",
    # Year only (we will explicitly ignore these later)
    r"\b(19|20)\d{2}\b",
    # Q1 2024, Q2 2023 etc
    r"\bQ[1-4][- ]?\d{4}\b",
]

DATE_MASTER_REGEX = re.compile("|".join(f"({r})" for r in DATE_REGEXPS), re.IGNORECASE)

# Relative time phrases
RELATIVE_PATTERNS = [
    ("yesterday", ("days", -1)),
    ("today", ("days", 0)),
    ("tomorrow", ("days", 1)),
    ("last week", ("weeks", -1)),
    ("last month", ("months", -1)),
    ("last year", ("years", -1)),
    ("this week", ("weeks", 0)),
    ("this month", ("months", 0)),
    ("this year", ("years", 0)),
    ("next week", ("weeks", 1)),
    ("next month", ("months", 1)),
    ("next year", ("years", 1)),
]

# Date range patterns (split to start/end)
RANGE_PATTERNS = [
    # April 19 to June 1, 2024
    re.compile(
        rf"\b({MONTHS})\s+(\d{{1,2}})\s+(?:to|-|–|—)\s+({MONTHS})\s+(\d{{1,2}})(?:,\s*(\d{{4}}))?\b",
        flags=re.IGNORECASE,
    ),
    # July 20–27, 2024 (same month)
    re.compile(
        rf"\b({MONTHS})\s+(\d{{1,2}})\s*(?:to|-|–|—)\s*(\d{{1,2}})(?:,\s*(\d{{4}}))?\b",
        flags=re.IGNORECASE,
    ),
]
