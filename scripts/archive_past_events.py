#!/usr/bin/env python3
"""Move past events from the upcoming carousel into the past-events widget.

Run nightly (or manually) by .github/workflows/update-community-events.yml.

Strategy
--------
We look for HTML blocks in `index.md` whose root tag carries a
`data-event-date="YYYY-MM-DD"` attribute. Anything older than
``today (UTC)`` and still living inside the upcoming carousel is:
  1. Removed from the carousel block.
  2. Re-rendered as a `<article class="past-event-item">` and inserted
     at the top of the `past-events-widget` section.

The script is idempotent — if no event has expired since the last run
it exits 0 without touching the file.
"""
from __future__ import annotations

import datetime as dt
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.md"

CAROUSEL_RE = re.compile(
    r'(<div class="event-grid event-carousel-track"[^>]*>)(.*?)(</div>\s*<button[^>]*data-carousel-next)',
    re.DOTALL,
)
PAST_HEADING_RE = re.compile(
    r'(<section class="side-widget past-events-widget">.*?<h2>Community archive</h2>)',
    re.DOTALL,
)
PAST_WIDGET_RE = re.compile(
    r'<section class="side-widget past-events-widget">.*?</section>',
    re.DOTALL,
)
EVENT_CARD_RE = re.compile(
    r'<article class="event-card"[^>]*data-event-date="(\d{4}-\d{2}-\d{2})"[^>]*>(.*?)</article>',
    re.DOTALL,
)
FEATURED_EVENT_RE = re.compile(
    r'\s*<section class="featured-event featured-event-upcoming"'
    r'[^>]*data-event-date="(\d{4}-\d{2}-\d{2})"[^>]*>(.*?)</section>\s*',
    re.DOTALL,
)
TITLE_RE = re.compile(r"<h[23]>(.*?)</h[23]>", re.DOTALL)
PARAGRAPH_RE = re.compile(
    r'<p(?:\s+class="([^"]*)")?>(.*?)</p>',
    re.DOTALL,
)
LINK_RE = re.compile(
    r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
    re.DOTALL,
)


PAST_ITEM_RE = re.compile(
    r'<article class="past-event-item[^"]*"[^>]*>.*?</article>',
    re.DOTALL,
)
VISIBLE_ITEMS_SHOWN = 2  # items shown before the "Show all" toggle


def render_past_item(date_iso: str, card_html: str, hidden: bool = False) -> str:
    """Convert an upcoming-card HTML body into a past-event-item block."""
    date_obj = dt.date.fromisoformat(date_iso)
    pretty = date_obj.strftime("%B %-d, %Y")  # macOS / Linux

    title_m = TITLE_RE.search(card_html)
    title = title_m.group(1).strip() if title_m else "Past event"
    desc = ""
    for css_class, paragraph in PARAGRAPH_RE.findall(card_html):
        if css_class in {"eyebrow", "event-date", "event-kicker"}:
            continue
        desc = paragraph.strip()
        break

    actions: list[str] = []
    for href, text in LINK_RE.findall(card_html):
        # Use the original Meetup link as "Event details" by default.
        link_text = re.sub(r"<[^>]+>", "", text).strip()
        label = "Event details" if "meetup.com" in href else link_text
        actions.append(
            f'          <a href="{href}" target="_blank" rel="noopener">{label}</a>'
        )
    # Always add a pointer to the community YouTube channel for recordings.
    actions.append(
        '          <a href="https://www.youtube.com/@MaltaMicrosoftAIUserGroupMMAUG"'
        ' target="_blank" rel="noopener">'
        "Catch up on the recording on our YouTube channel</a>"
    )
    actions_html = "\n".join(actions)

    hidden_class = " past-event-hidden" if hidden else ""
    return (
        f'      <article class="past-event-item{hidden_class}" data-event-date="{date_iso}">\n'
        f'        <p class="event-kicker">{pretty}</p>\n'
        f'        <h3>{title}</h3>\n'
        f'        <p>{desc}</p>\n'
        f'        <div class="past-event-actions">\n'
        f'{actions_html}\n'
        f'        </div>\n'
        f'      </article>'
    )


def event_identity(date_iso: str, event_html: str) -> tuple[str, str]:
    """Return a stable identity that also catches featured/card duplicates."""
    title_m = TITLE_RE.search(event_html)
    title = re.sub(r"\s+", " ", title_m.group(1)).strip().casefold() if title_m else ""
    meetup_links = [href for href, _ in LINK_RE.findall(event_html) if "meetup.com" in href]
    return date_iso, meetup_links[0] if meetup_links else title


def normalize_past_item_visibility(widget_html: str) -> str:
    """Show the newest items and hide the rest inside the archive widget."""
    position = 0

    def _set_visibility(match: re.Match[str]) -> str:
        nonlocal position
        item = match.group(0)
        css_class = (
            "past-event-item"
            if position < VISIBLE_ITEMS_SHOWN
            else "past-event-item past-event-hidden"
        )
        position += 1
        return re.sub(
            r'class="past-event-item(?:\s+past-event-hidden)?"',
            f'class="{css_class}"',
            item,
            count=1,
        )

    return PAST_ITEM_RE.sub(_set_visibility, widget_html)


def archive_events(text: str, today: dt.date) -> tuple[str, list[str]]:
    """Archive expired carousel/featured events and return updated HTML."""
    carousel_m = CAROUSEL_RE.search(text)
    if not carousel_m:
        raise ValueError("could not locate upcoming-events carousel block")

    expired: list[tuple[str, str]] = []

    def _take_card(match: re.Match[str]) -> str:
        date_iso = match.group(1)
        if dt.date.fromisoformat(date_iso) < today:
            expired.append((date_iso, match.group(0)))
            return ""
        return match.group(0)

    new_carousel_inner = EVENT_CARD_RE.sub(_take_card, carousel_m.group(2))
    new_carousel_inner = re.sub(r"\n\s*\n\s*\n", "\n\n", new_carousel_inner)
    text = text[: carousel_m.start(2)] + new_carousel_inner + text[carousel_m.end(2) :]

    expired_identities = {event_identity(date_iso, item) for date_iso, item in expired}

    def _take_featured(match: re.Match[str]) -> str:
        date_iso = match.group(1)
        if dt.date.fromisoformat(date_iso) >= today:
            return match.group(0)
        identity = event_identity(date_iso, match.group(0))
        if identity not in expired_identities:
            expired.append((date_iso, match.group(0)))
            expired_identities.add(identity)
        return "\n"

    text = FEATURED_EVENT_RE.sub(_take_featured, text)

    if not expired:
        return text, []

    past_m = PAST_HEADING_RE.search(text)
    widget_m = PAST_WIDGET_RE.search(text)
    if not past_m or not widget_m:
        raise ValueError("could not locate past-events widget")

    existing_identities: set[tuple[str, str]] = set()
    for item_m in PAST_ITEM_RE.finditer(widget_m.group(0)):
        date_m = re.search(r'data-event-date="(\d{4}-\d{2}-\d{2})"', item_m.group(0))
        if date_m:
            existing_identities.add(event_identity(date_m.group(1), item_m.group(0)))

    expired.sort(key=lambda item: item[0], reverse=True)
    new_items = [
        render_past_item(date_iso, event_html)
        for date_iso, event_html in expired
        if event_identity(date_iso, event_html) not in existing_identities
    ]

    if new_items:
        insertion_point = past_m.end()
        text = text[:insertion_point] + "\n" + "\n".join(new_items) + text[insertion_point:]

    widget_m = PAST_WIDGET_RE.search(text)
    if not widget_m:
        raise ValueError("could not locate past-events widget after update")
    normalized_widget = normalize_past_item_visibility(widget_m.group(0))
    text = text[: widget_m.start()] + normalized_widget + text[widget_m.end() :]
    return text, [date_iso for date_iso, _ in expired]


def main() -> int:
    today = dt.date.today()
    text = INDEX.read_text()
    try:
        updated, archived_dates = archive_events(text, today)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if updated == text:
        print(f"no expired upcoming events as of {today.isoformat()}")
        return 0

    INDEX.write_text(updated)
    moved = ", ".join(archived_dates)
    print(f"archived {len(archived_dates)} event(s): {moved}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
