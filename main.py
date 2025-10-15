import argparse
from datetime import datetime
from colorama import init as colorama_init, Fore, Style

from modules.scraper import fetch_article
from modules.date_extractor import extract_date_mentions
from modules.event_extractor import split_sentences, sentences_with_dates, cluster_events
from modules.event_summarizer import summarize_event
from modules.timeline_builder import build_timeline, to_export_rows
from modules.io_utils import save_json, save_csv


def main():
    colorama_init(autoreset=True)

    parser = argparse.ArgumentParser(description="Timeline Extraction from a news URL (No LLM, Rule-Based)")
    parser.add_argument("--url", required=True, help="News article URL to extract timeline from")
    parser.add_argument("--window", type=int, default=0, help="Context window for merging nearby sentences")
    parser.add_argument("--out", default="timeline.json", help="Output JSON file")
    parser.add_argument("--csv", default=None, help="Optional CSV output path")
    args = parser.parse_args()

    print(f"\n{Fore.CYAN}🔎 Fetching article from URL:{Style.RESET_ALL} {args.url}")
    article = fetch_article(args.url)

    if not article or not article["text"]:
        print(f"{Fore.RED}❌ Failed to extract article text. Try another URL.{Style.RESET_ALL}")
        return

    text = article["text"]
    ref_date = article["published_at"] or datetime.now()

    print(f"{Fore.GREEN}✅ Article fetched successfully.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}✂️ Splitting into sentences & filtering noise...{Style.RESET_ALL}")
    sentences = split_sentences(text)

    print(f"{Fore.CYAN}📅 Extracting date mentions (incl. ranges)...{Style.RESET_ALL}")
    mentions = extract_date_mentions(text, ref_date=ref_date)
    if not mentions:
        print(f"{Fore.RED}❌ No valid dates found in the article. Cannot build a timeline.{Style.RESET_ALL}")
        return
    print(f"{Fore.GREEN}✅ Found {len(mentions)} date mentions.{Style.RESET_ALL}")

    print(f"{Fore.CYAN}🔗 Mapping dates to sentences & pairing headlines...{Style.RESET_ALL}")
    hits = sentences_with_dates(sentences, mentions)

    print(f"{Fore.CYAN}🧱 Building event blocks...{Style.RESET_ALL}")
    events = cluster_events(sentences, hits, window=args.window)

    print(f"{Fore.CYAN}🧽 Cleaning & summarizing event lines...{Style.RESET_ALL}")
    for e in events:
        e["text"] = summarize_event(e["text"])

    # Strict Mode: keep only events that HAVE a date
    events = [e for e in events if e["date"]]

    print(f"{Fore.CYAN}📊 Building final timeline...{Style.RESET_ALL}")
    timeline = build_timeline(events)
    rows = to_export_rows(timeline)

    result = {
        "source_title": article["title"],
        "source_url": article["url"],
        "reference_date": ref_date.strftime("%Y-%m-%d"),
        "count": len(rows),
        "timeline": rows,
    }

    print(f"{Fore.YELLOW}💾 Saving JSON → {args.out}{Style.RESET_ALL}")
    save_json(result, args.out)

    if args.csv:
        print(f"{Fore.YELLOW}💾 Saving CSV  → {args.csv}{Style.RESET_ALL}")
        save_csv(rows, args.csv)

    print(f"\n{Fore.GREEN}✅ Timeline extraction complete!{Style.RESET_ALL}\n")
    print(f"{Fore.MAGENTA}🕒 Final Timeline Preview:{Style.RESET_ALL}")
    print("-----------------------------------")
    for item in rows[:10]:  # preview first 10
        print(f"{Fore.BLUE}{item['date']}{Style.RESET_ALL} → {item['event']}")
    print("-----------------------------------")
    print(f"{Fore.CYAN}📦 Total Events:{Style.RESET_ALL} {len(rows)}")
    print(f"{Fore.CYAN}📁 JSON:{Style.RESET_ALL} {args.out}")
    if args.csv:
        print(f"{Fore.CYAN}📁 CSV :{Style.RESET_ALL} {args.csv}")


if __name__ == "__main__":
    main()
