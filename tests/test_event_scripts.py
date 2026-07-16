import datetime as dt
import json
import unittest

from scripts.archive_past_events import archive_events
from scripts.sync_upcoming_meetup_events import extract_upcoming_events


def homepage_fixture(*, featured: str = "", cards: str = "") -> str:
    return f"""---
layout: default
---
{featured}
<div class="event-grid event-carousel-track" data-carousel-track>
{cards}
</div>
<button data-carousel-next>Next</button>
<section class="side-widget past-events-widget">
  <h2>Community archive</h2>
  <article class="past-event-item" data-event-date="2026-07-08">
    <p class="event-kicker">July 8, 2026</p><h3>Older event</h3><p>Older.</p>
  </article>
  <article class="past-event-item" data-event-date="2026-07-01">
    <p class="event-kicker">July 1, 2026</p><h3>Oldest event</h3><p>Oldest.</p>
  </article>
  <button data-past-events-toggle>Show all</button>
</section>
"""


def event_card(date_iso: str, title: str, event_id: str) -> str:
    return f"""<article class="event-card" data-event-date="{date_iso}">
  <p class="event-kicker">Jul 10</p>
  <h3>{title}</h3>
  <p>Event description.</p>
  <a href="https://www.meetup.com/example/events/{event_id}/">View event</a>
</article>"""


class ArchiveEventsTests(unittest.TestCase):
    def test_archives_expired_card_removes_duplicate_featured_and_shows_newest(self):
        expired_card = event_card("2026-07-10", "Expired event", "100")
        future_card = event_card("2026-07-20", "Future event", "200")
        featured = """<section class="featured-event featured-event-upcoming" data-event-date="2026-07-10">
  <p class="eyebrow">Featured Event</p>
  <h2>Expired event</h2>
  <p class="event-date">July 10, 2026</p>
  <p>Featured description.</p>
  <a class="primary-action" href="https://www.meetup.com/example/events/100/">Register</a>
</section>"""

        updated, archived = archive_events(
            homepage_fixture(featured=featured, cards=expired_card + future_card),
            dt.date(2026, 7, 15),
        )

        self.assertEqual(archived, ["2026-07-10"])
        self.assertNotIn("featured-event-upcoming", updated)
        self.assertNotIn('class="event-card" data-event-date="2026-07-10"', updated)
        self.assertIn('class="event-card" data-event-date="2026-07-20"', updated)
        self.assertEqual(updated.count("<h3>Expired event</h3>"), 1)
        self.assertIn(
            'class="past-event-item" data-event-date="2026-07-10"', updated
        )
        self.assertIn(
            'class="past-event-item" data-event-date="2026-07-08"', updated
        )
        self.assertIn(
            'class="past-event-item past-event-hidden" data-event-date="2026-07-01"',
            updated,
        )

        second_update, second_archived = archive_events(updated, dt.date(2026, 7, 15))
        self.assertEqual(second_update, updated)
        self.assertEqual(second_archived, [])

    def test_archives_featured_event_that_is_not_in_carousel(self):
        featured = """<section class="featured-event featured-event-upcoming" data-event-date="2026-07-09">
  <h2>Featured only</h2><p>Featured description.</p>
  <a href="https://www.meetup.com/example/events/300/">Register</a>
</section>"""

        updated, archived = archive_events(
            homepage_fixture(featured=featured), dt.date(2026, 7, 15)
        )

        self.assertEqual(archived, ["2026-07-09"])
        self.assertIn("<h3>Featured only</h3>", updated)
        self.assertNotIn("featured-event-upcoming", updated)


class SyncMeetupEventsTests(unittest.TestCase):
    def test_excludes_past_and_inactive_events(self):
        connection_key = (
            'events({"filter":{"afterDateTime":"2026-01-01"},"sort":"ASC"})'
        )
        state = {
            "ROOT_QUERY": {
                'groupByUrlname:{"urlname":"malta-microsoft-ai-user-group"}': {
                    "__ref": "Group:1"
                }
            },
            "Group:1": {
                connection_key: {
                    "edges": [
                        {"node": {"__ref": "Event:past"}},
                        {"node": {"__ref": "Event:future"}},
                        {"node": {"__ref": "Event:cancelled"}},
                    ]
                }
            },
            "Event:past": {
                "status": "ACTIVE",
                "dateTime": "2026-07-10T18:00:00+02:00",
                "title": "Past event",
                "description": "Already happened.",
                "eventUrl": "https://www.meetup.com/example/events/past/",
            },
            "Event:future": {
                "status": "ACTIVE",
                "dateTime": "2026-07-20T18:00:00+02:00",
                "title": "Future event",
                "description": "Still upcoming.",
                "eventUrl": "https://www.meetup.com/example/events/future/",
            },
            "Event:cancelled": {
                "status": "CANCELLED",
                "dateTime": "2026-07-21T18:00:00+02:00",
                "title": "Cancelled event",
                "description": "Cancelled.",
                "eventUrl": "https://www.meetup.com/example/events/cancelled/",
            },
        }
        payload = {"props": {"pageProps": {"__APOLLO_STATE__": state}}}
        meetup_html = (
            '<script id="__NEXT_DATA__" type="application/json">'
            + json.dumps(payload)
            + "</script>"
        )

        events = extract_upcoming_events(meetup_html, dt.date(2026, 7, 15))

        self.assertEqual([event["title"] for event in events], ["Future event"])
        self.assertEqual(events[0]["date_iso"], "2026-07-20")


if __name__ == "__main__":
    unittest.main()
