REF_YEAR_TOLERANCE_FUTURE = 1   # allow up to ref_year + 1

MIN_EVENT_LEN_CHARS = 40
MAX_EVENT_LEN_CHARS = 260

# Sentences containing any of these will be dropped (site chrome etc.)
IGNORE_IF_CONTAINS = {
    "you might also like", "subscribe to", "read more", "adblock", "newsletter",
    "watch:", "click here", "prime benefits", "e-paper", "view all", "live blog",
    "trending now", "top videos", "install app", "benchmarks", "nifty", "sensex"
}

# Drop if the whole sentence matches these
DROP_SENTENCE_IF_MATCHES = {
    r"^\d+\s+\d+\s+\d+$",              # "1 2 3"
    r"^\s*more\s+less\s*$",
    r"^\s*(view|watch|read)\s+all.*$",
}

TRIM_AFTER_TOKENS = [" You Might Also Like", " (Catch all", " Read More", " Subscribe to ", " …", " ..."]

# Headline/section detection + pairing
HEADLINE_MAX_LEN = 140
HEADLINE_MIN_WORDS = 3
PROXIMITY_WINDOW = 3  # how many sentences around a headline to search for nearby dates
