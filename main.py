import argparse
from datetime import datetime
from colorama import init, Fore, Style

from modules.scraper import fetch_article
from modules.date_extractor import extract_date_mentions
from modules.event_extractor import split_sentences, sentences_with_dates, cluster_events
from modules.list_mode import split_list_items, build_events_from_items
from modules.timeline_builder import build_timeline, to_export_rows
from modules.io_utils import save_json, save_csv
from modules.event_summarizer import summarize_event

init(autoreset=True)

def main():
    parser = argparse.ArgumentParser(description="Timeline Extractor - TOI compatible version (no AI)")
    parser.add_argument("--url", required=True, help="News article URL")
    parser.add_argument("--window", default=1, type=int, help="Context lines to include")
    parser.add_argument("--out", default="timeline.json", help="Output JSON file")
    parser.add_argument("--csv", default=None, help="Optional CSV export path")
    args = parser.parse_args()

    print(f"{Fore.CYAN}🔎 Fetching article... {Style.RESET_ALL}{args.url}")
    article = fetch_article(args.url)

    if not article["text"]:
        print(f"{Fore.RED}❌ Failed to extract article text.{Style.RESET_ALL}")
        return

    text = article["text"]
    title = article["title"]
    ref_date = article["published_at"] or datetime.now()

    # ✅ Detect list-style articles
    items = split_list_items(text)
    if len(items) >= 3:  # treat as bullet/list article
        print(f"{Fore.YELLOW}📝 Detected List Article → Extracting all points...{Style.RESET_ALL}")
        events = build_events_from_items(items, ref_date)
    else:
        print(f"{Fore.GREEN}📘 Normal article detected → Sentence extraction{Style.RESET_ALL}")
        sentences = split_sentences(text)
        mentions = extract_date_mentions(text, ref_date)
        hits = sentences_with_dates(sentences, mentions)
        events = cluster_events(sentences, hits, window=args.window)
        for e in events:
            e["text"] = summarize_event(e["text"])
            if "year" not in e:
                e["year"] = None

    # 📌 Fallback when no events parsed
    if not events:
        print(f"{Fore.YELLOW}⚠ No events found, adding article headline as event{Style.RESET_ALL}")
        events = [{
            "date": article["published_at"],
            "year": None,
            "text": summarize_event(title),
            "surface": "article_header",
            "anchor_sentence_index": -1
        }]

    # 🛠 Build final timeline
    final_timeline = build_timeline(events)
    rows = to_export_rows(final_timeline)

    result = {
        "source_title": article["title"],
        "source_url": article["url"],
        "reference_date": ref_date.strftime("%Y-%m-%d"),
        "count": len(rows),
        "timeline": rows
    }

    save_json(result, args.out)
    if args.csv:
        save_csv(rows, args.csv)

    print(f"{Fore.GREEN}✅ Done! Extracted {len(rows)} timeline events.{Style.RESET_ALL}")
    print(f"💾 Output saved as: {args.out}")
    if args.csv:
        print(f"📄 CSV saved as: {args.csv}")

if __name__ == "__main__":
    main()
