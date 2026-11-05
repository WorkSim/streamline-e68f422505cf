"""Grading suite for DATA-509 — UTC-correct timestamp parsing + day bucketing.

Acceptance criteria:
  - Timestamps are parsed as UTC (tz-aware), never host-local.
  - Naive timestamps (no offset/Z) are treated as already-UTC.
  - Day bucketing uses the UTC calendar date, so near-midnight and
    offset/DST rows land in the correct UTC day, not a locally-shifted one.
"""

from datetime import timezone

from streamline.timestamps import parse_utc, utc_day_bucket


def test_parse_utc_returns_tz_aware_utc_datetime():
    parsed = parse_utc("2026-07-26T08:00:00Z")

    assert parsed.tzinfo is not None
    assert parsed.utcoffset().total_seconds() == 0
    assert parsed.tzinfo == timezone.utc


def test_parse_utc_naive_input_is_not_shifted_by_host_local():
    # A naive timestamp must be interpreted as UTC directly — the parsed
    # wall-clock hour must match the input hour exactly, regardless of the
    # host machine's local timezone.
    parsed = parse_utc("2026-07-26T08:15:30")

    assert parsed.tzinfo == timezone.utc
    assert (parsed.hour, parsed.minute, parsed.second) == (8, 15, 30)


def test_parse_utc_normalizes_positive_offset_to_utc():
    parsed = parse_utc("2026-07-26T08:00:00+09:00")

    assert parsed.tzinfo == timezone.utc
    assert parsed.hour == 23
    assert parsed.day == 25


def test_parse_utc_normalizes_negative_offset_to_utc():
    parsed = parse_utc("2026-07-26T08:00:00-04:00")

    assert parsed.tzinfo == timezone.utc
    assert parsed.hour == 12
    assert parsed.day == 26


def test_utc_day_bucket_row_just_before_utc_midnight_stays_previous_day():
    assert utc_day_bucket("2026-07-26T23:59:59Z") == "2026-07-26"


def test_utc_day_bucket_row_just_after_utc_midnight_is_next_day():
    assert utc_day_bucket("2026-07-27T00:00:01Z") == "2026-07-27"


def test_utc_day_bucket_positive_offset_rolls_back_a_day():
    # 2026-07-27T02:00:00+09:00 is 2026-07-26T17:00:00Z.
    assert utc_day_bucket("2026-07-27T02:00:00+09:00") == "2026-07-26"


def test_utc_day_bucket_negative_offset_rolls_forward_a_day():
    # 2026-07-26T22:00:00-04:00 is 2026-07-27T02:00:00Z.
    assert utc_day_bucket("2026-07-26T22:00:00-04:00") == "2026-07-27"


def test_utc_day_bucket_naive_timestamp_treated_as_utc_day():
    assert utc_day_bucket("2026-07-26T23:59:59") == "2026-07-26"
