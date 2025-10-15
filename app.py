from flask import Flask, render_template, request
from datetime import datetime
from modules.scraper import fetch_article
from modules.list_mode import split_list_items, build_events_from_items
from modules.event_extractor import split_sentences, sentences_with_dates, cluster_events
from modules.timeline_builder import build_timeline, to_export_rows
from modules.event_summarizer import summarize_event
from modules.date_extractor import extract_date_mentions

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    timeline = []
    title = None
    error = None

    if request.method == "POST":
        url = request.form.get("url")
        try:
            article = fetch_article(url)
            title = article["title"]
            text = article["text"]
            ref_date = article["published_at"] or datetime.now()

            items = split_list_items(text)

            if len(items) >= 3:  # List article mode
                events = build_events_from_items(items, ref_date)
            else:  # Normal article mode
                sentences = split_sentences(text)
                mentions = extract_date_mentions(text, ref_date)
                hits = sentences_with_dates(sentences, mentions)
                events = cluster_events(sentences, hits)

                for e in events:
                    e["text"] = summarize_event(e["text"])
                    if "year" not in e:
                        e["year"] = None

            timeline = to_export_rows(build_timeline(events))

        except Exception as e:
            error = str(e)

    return render_template("index.html", timeline=timeline, title=title, error=error)

if __name__ == "__main__":
    app.run(debug=True)
