# General Settings
REF_YEAR_TOLERANCE_FUTURE = 1  # Allow 1 year into future max

# Sentence filtering
MIN_EVENT_LEN_CHARS = 40
MAX_EVENT_LEN_CHARS = 260

IGNORE_IF_CONTAINS = {
    "you might also like", "subscribe to", "read more", "adblock", "newsletter",
    "watch:", "click here", "prime benefits", "e-paper", "view all", "live blog",
    "trending now", "top videos", "install app", "benchmarks", "nifty", "sensex",
    "etprime", "follow us", "comment", "share", "timespoints", "gadgets now",
    "sign in", "etimes", "entertainment news", "trending now", "copyright"
}

DROP_SENTENCE_IF_MATCHES = {
    r"^\d+\s+\d+\s+\d+$",
    r"^\s*more\s+less\s*$",
    r"^\s*(view|watch|read)\s+all.*$",
}

TRIM_AFTER_TOKENS = [" You Might Also Like", " (Catch all", " Read More", " Subscribe to ", " …", " ..."]

# Headline detection rules
HEADLINE_MAX_LEN = 140
HEADLINE_MIN_WORDS = 3
PROXIMITY_WINDOW = 3

# Event Ranking
SCORE_HEADLINE_BONUS = 2.0
SCORE_VERB_WEIGHT = 0.8
SCORE_PROPN_WEIGHT = 0.6
SCORE_LEN_CAP = 1.5
