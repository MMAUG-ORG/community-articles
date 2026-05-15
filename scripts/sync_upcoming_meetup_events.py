#!/usr/bin/env python3
"""Sync the homepage upcoming-events carousel from the Meetup group page."""
from __future__ import annotations

import datetime as dt
import html
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.md"
GROUP_URL = "https://www.meetup.com/malta-microsoft-ai-user-group/events/"
GROUP_URLNAME = "malta-microsoft-ai-user-group"
MAX_EVENTS = 6

CAROUSEL_RE = re.compile(
    r'(<div class="event-grid event-carousel-track"[^>]*>)(.*?)(</div>\s*<button[^>]*data-carousel-next)',
    re.DOTALL,
)
NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)


def fetch_html(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; MMAUG-upcoming-events-sync/1.0)"
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def extract_upcoming_events(html_text: str) -> list[dict[str, str]]:
    next_data_match = NEXT_DATA_RE.search(html_text)
    if not next_data_match:
        raise RuntimeError("could not locate __NEXT_DATA__ payload on Meetup page")

    payload = json.loads(next_data_match.group(1))
    state = payload["props"]["pageProps"]["__APOLLO_STATE__"]
    root_query = state["ROOT_QUERY"]
    group_key = f'groupByUrlname:{{"urlname":"{GROUP_URLNAME}"}}'
    group_ref = root_query[group_key]["__ref"]
    group = state[group_ref]

    event_connection = None
    for key, value in group.items():
        if not key.startswith('events({"filter":{"afterDateTime":'):
            continue
        if '"sort":"ASC"' not in key:
            continue
        event_connection = value
        break

    if event_connection is None:
        raise RuntimeError("could not locate upcoming events connection in Meetup data")

    events: list[dict[str, str]] = []
    for edge in event_connection.get("edges", []):
        ref = edge["node"]["__ref"]
        event = state[ref]
        if event.get("status") != "ACTIVE":
            continue

        when = dt.datetime.fromisoformat(event["dateTime"])
        events.append(
            {
                "date_iso": when.date().isoformat(),
                "kicker": f"{when.strftime('%b')} {when.day}",
                "title": event["title"].strip(),
                "description": summarize_description(event.get("description", "")),
                "url": event["eventUrl"],
            }
        )

    return events[:MAX_EVENTS]


def summarize_description(raw: str) -> str:
    text = re.sub(r"\s+", " ", raw).strip()
    if not text:
        return "View event details on Meetup."

    sentence_match = re.match(r"(.{1,200}?[.!?])(?:\s|$)", text)
    if sentence_match:
        return sentence_match.group(1).strip()

    if len(text) <= 180:
        return text

    cut = text[:177].rsplit(" ", 1)[0].strip()
    return f"{cut}..."


def render_event_card(event: dict[str, str]) -> str:
    title = html.escape(event["title"])
    description = html.escape(event["description"])
    url = html.escape(event["url"], quote=True)

    return (
        f'    <article class="event-card" data-event-date="{event["date_iso"]}">\n'
        f'      <p class="event-kicker">{event["kicker"]}</p>\n'
        f"      <h3>{title}</h3>\n"
        f"      <p>{description}</p>\n"
        f'      <a href="{url}" target="_blank" rel="noopener">View event</a>\n'
        f"    </article>"
    )


def main() -> int:
    html_text = fetch_html(GROUP_URL)
    events = extract_upcoming_events(html_text)
    if not events:
        raise RuntimeError("Meetup page returned no active upcoming events")

    new_inner = "\n".join(render_event_card(event) for event in events)
    text = INDEX.read_text()
    carousel_match = CAROUSEL_RE.search(text)
    if not carousel_match:
        raise RuntimeError("could not locate homepage upcoming-events carousel block")

    updated = text[: carousel_match.start(2)] + "\n" + new_inner + "\n    " + text[carousel_match.end(2) :]
    if updated != text:
        INDEX.write_text(updated)
        print(f"synced {len(events)} upcoming Meetup event(s)")
    else:
        print(f"upcoming Meetup events already up to date ({len(events)} item(s))")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # pragma: no cover - workflow error path
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
