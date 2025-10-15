# 🗓 News Timeline Extractor

Extraction of chronological timelines from news articles. The tool processes article text, identifies dates and events, and presents them in a clean, sorted timeline format.

## Features

- **Automatic Date Extraction**: Recognizes various date formats (absolute, relative, and ranges)
- **Dual Processing Modes**: 
  - **List Mode**: For articles with numbered/bulleted lists
  - **Normal Mode**: For standard news articles with flowing text
- **Smart Event Detection**: Uses NLP to identify and cluster related events
- **Year-Only Support**: Handles events with only year information
- **Timeline Deduplication**: Removes duplicate events automatically
- **Clean Output**: Summarizes events into concise, readable entries

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd news-timeline-extractor
```

2. Install required dependencies:
```bash
pip install flask requests beautifulsoup4 lxml spacy python-dateutil
python -m spacy download en_core_web_sm
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Enter a news article URL in the input field
2. Click "Extract Timeline"
3. View the chronologically sorted timeline of events

The application will automatically:
- Fetch and parse the article content
- Extract dates and events
- Sort them chronologically
- Display them in a clean table format

## Project Structure

```
news-timeline-extractor/
├── app.py                      # Main Flask application
├── templates/
│   └── index.html             # Web interface
└── modules/
    ├── scraper.py             # Article fetching and parsing
    ├── date_extractor.py      # Date recognition and normalization
    ├── date_patterns.py       # Regex patterns for date matching
    ├── event_extractor.py     # Event detection and clustering
    ├── event_summarizer.py    # Event text summarization
    ├── list_mode.py           # List-based article processing
    ├── timeline_builder.py    # Timeline sorting and deduplication
    ├── io_utils.py            # File I/O utilities
    └── settings.py            # Configuration parameters
```

## How It Works

### 1. Article Scraping
- Fetches article content using `requests` and `BeautifulSoup`
- Extracts clean text from JSON-LD metadata (for supported sites like TOI)
- Falls back to HTML parsing for other sites

### 2. Date Extraction
- **Absolute dates**: Jan 12, 2024 | 12 March 2023 | 2024-06-04
- **Relative dates**: yesterday, last week, next month
- **Date ranges**: April 19 to June 1, 2024
- **Years**: Standalone year mentions (1990-2025)
- Uses both regex patterns and spaCy NER for robust extraction

### 3. Event Processing

**List Mode** (for articles with 3+ list items):
- Splits article into bullet points or numbered items
- Extracts dates/years from each item
- Summarizes each item as a separate event

**Normal Mode** (for standard articles):
- Splits text into sentences using spaCy
- Matches sentences containing dates
- Identifies headline-like sentences near dates
- Clusters related sentences into events
- Summarizes each event cluster

### 4. Timeline Building
- Deduplicates events based on date/year and text
- Sorts events chronologically:
  1. Events with full dates (earliest first)
  2. Events with only years
  3. Undated events (last)

## Configuration

Key settings in `modules/settings.py`:

```python
# Event filtering
MIN_EVENT_LEN_CHARS = 40        # Minimum event text length
MAX_EVENT_LEN_CHARS = 260       # Maximum event text length

# Headline detection
HEADLINE_MAX_LEN = 140          # Max length for headline detection
HEADLINE_MIN_WORDS = 3          # Min words for headline detection
PROXIMITY_WINDOW = 3            # Sentence window for event clustering

# Date extraction
REF_YEAR_TOLERANCE_FUTURE = 1   # Allow dates up to 1 year in future
```

## Supported Date Formats

- **Month Day, Year**: January 15, 2024
- **Day Month Year**: 15 January 2024
- **ISO Format**: 2024-01-15
- **Month Year**: January 2024
- **Quarters**: Q3 2023
- **Relative**: yesterday, last week, next month
- **Ranges**: April 19 to June 1, 2024

## Output Format

The timeline table contains three columns:

| Column | Description |
|--------|-------------|
| **Date** | Full date in YYYY-MM-DD format (if available) |
| **Year** | Year only (for events without specific dates) |
| **Event** | Summarized event description |

## Dependencies

- **Flask**: Web framework
- **requests**: HTTP library for fetching articles
- **BeautifulSoup4**: HTML parsing
- **lxml**: XML/HTML parser
- **spaCy**: NLP for sentence splitting and NER
- **python-dateutil**: Flexible date parsing

## Limitations

- Requires internet connection to fetch articles
- Some paywalled content may not be accessible
- Date extraction accuracy depends on article formatting
- Best suited for English-language news articles