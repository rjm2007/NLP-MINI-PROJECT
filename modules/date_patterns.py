import re

# Supports month names for date extraction
MONTHS = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?" \
         r"|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"

# Regex patterns to catch dates like:
# - Jan 12, 2024
# - 12 March 2023
# - 2024-06-04
# - March 2024
# - Q3 2022
DATE_REGEXPS = [
    rf"\b{MONTHS}\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,)?\s+\d{{4}}\b",
    rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+{MONTHS}\s+\d{{4}}\b",
    r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",
    rf"\b{MONTHS}\s+\d{{4}}\b",
    r"\bQ[1-4][- ]?\d{4}\b"
]

# Join into one mega regex
DATE_MASTER_REGEX = re.compile("|".join(f"({r})" for r in DATE_REGEXPS), re.IGNORECASE)

# Relative date patterns
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

# Date ranges like:
# - April 19 to June 1, 2024
# - July 20–27, 2024
RANGE_PATTERNS = [
    re.compile(
        rf"\b({MONTHS})\s+(\d{{1,2}})\s+(?:to|-|–|—)\s+({MONTHS})\s+(\d{{1,2}})(?:,\s*(\d{{4}}))?\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        rf"\b({MONTHS})\s+(\d{{1,2}})\s*(?:to|-|–|—)\s*(\d{{1,2}})(?:,\s*(\d{{4}}))?\b",
        flags=re.IGNORECASE,
    ),
]
