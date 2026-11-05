"""UTC-correct timestamp parsing and day bucketing.

Source rows carry ISO-8601 timestamp strings. Every timestamp must be
interpreted as UTC (never host-local) so that day bucketing is stable across
machines and near-midnight rows land in the correct UTC day.
"""

from __future__ import annotations

from datetime import datetime, timezone


def parse_utc(ts: str) -> datetime:
    """Parse an ISO-8601 timestamp string as UTC.

    Accepts the trailing `Z` UTC designator (translated to `+00:00` for
    `datetime.fromisoformat`). Naive timestamps (no offset, no `Z`) are
    treated as already being in UTC — they are never interpreted as
    host-local time. Timestamps with an explicit non-UTC offset are
    converted to UTC.

    Args:
        ts: An ISO-8601 timestamp string, e.g. "2026-07-26T23:58:00Z" or
            "2026-07-26T23:58:00+05:00" or "2026-07-26T23:58:00".

    Returns:
        A timezone-aware `datetime` in UTC.
    """
    normalized = ts[:-1] + "+00:00" if ts.endswith("Z") else ts
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed
    return parsed.astimezone()


def utc_day_bucket(ts: str) -> str:
    """Return the `YYYY-MM-DD` UTC calendar date for a timestamp string.

    Built on `parse_utc`, so bucketing is always by UTC date regardless of
    the offset (if any) present in the input string.

    Args:
        ts: An ISO-8601 timestamp string.

    Returns:
        The UTC date as `YYYY-MM-DD`.
    """
    return parse_utc(ts).date().isoformat()
