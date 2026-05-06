#!/usr/bin/env python3
"""Move past events from the upcoming carousel into the past-events widget.

Run nightly (or manually) by .github/workflows/archive-past-events.yml.

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
EVENT_CARD_RE = re.compile(
    r'<article class="event-card"[^>]*data-event-date="(\d{4}-\d{2}-\d{2})"[^>]*>(.*?)</article>',
    re.DOTALL,
)
TITLE_RE = re.compile(r"<h3>(.*?)</h3>", re.DOTALL)
DESC_RE = re.compile(r"<p>(?!<)(.*?)</p>", re.DOTALL)
LINK_RE = re.compile(r'<a href="([^"]+)"[^>]*>([^<]+)</a>')


def render_past_item(date_iso: str, card_html: str) -> str:
    """Convert an upcoming-card HTML body into a past-event-item block."""
    date_obj = dt.date.fromisoformat(date_iso)
    pretty = date_obj.strftime("%B %-d, %Y")  # macOS / Linux

    title_m = TITLE_RE.search(card_html)
    desc_m = DESC_RE.search(card_html)
    title = title_m.group(1).strip() if title_m else "Past event"
    desc = desc_m.group(1).strip() if desc_m else ""

    actions: list[str] = []
    for href, text in LINK_RE.findall(card_html):
        # Use the original Meetup link as "Event details" by default.
        label = "Event details" if "meetup.com" in href else text.strip()
        actions.append(
            f'          <a href="{href}" target="_blank" rel="noopener">{label}</a>'
        )
    actions_html = "\n".join(actions) if actions else ""

    return (
        f'      <article class="past-event-item" data-event-date="{date_iso}">\n'
        f'        <p class="event-kicker">{pretty}</p>\n'
        f'        <h3>{title}</h3>\n'
        f'        <p>{desc}</p>\n'
        f'        <div class="past-event-actions">\n'
        f'{actions_html}\n'
        f'        </div>\n'
        f'      </article>'
    )


def main() -> int:
    today = dt.date.today()
    text = INDEX.read_text()

    carousel_m = CAROUSEL_RE.search(text)
    if not carousel_m:
        print("error: could not locate upcoming-events carousel block", file=sys.stderr)
        return 2

    carousel_inner = carousel_m.group(2)
    expired: list[tuple[str, str]] = []  # (date_iso, full_card_html)

    def _take(match: re.Match[str]) -> str:
        date_iso = match.group(1)
        if dt.date.fromisoformat(date_iso) < today:
            expired.append((date_iso, match.group(0)))
            return ""  # remove from upcoming
        return match.group(0)

    new_carousel_inner = EVENT_CARD_RE.sub(_take, carousel_inner)

    if not expired:
        print(f"no expired upcoming events as of {today.isoformat()}")
        return 0

    # Tidy whitespace inside carousel
    new_carousel_inner = re.sub(r"\n\s*\n\s*\n", "\n\n", new_carousel_inner)
    text = (
        text[: carousel_m.start(2)]
        + new_carousel_inner
        + text[carousel_m.end(2):]
    )

    # Build past-event blocks (newest first)
    expired.sort(key=lambda t: t[0], reverse=True)
    past_blocks = "\n".join(
        render_past_item(date_iso, card) for date_iso, card in expired
    )

    past_m = PAST_HEADING_RE.search(text)
    if not past_m:
        print("error: could not locate past-events widget", file=sys.stderr)
        return 3
    insertion_point = past_m.end()
    text = text[:insertion_point] + "\n" + past_blocks + text[insertion_point:]

    INDEX.write_text(text)
    moved = ", ".join(d for d, _ in expired)
    print(f"archived {len(expired)} event(s): {moved}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
