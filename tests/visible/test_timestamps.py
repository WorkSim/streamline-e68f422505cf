"""Visible tests for streamline.timestamps — develop against these."""

from datetime import timezone

from streamline.timestamps import parse_utc, utc_day_bucket


def test_parse_utc_handles_z_suffix():
    parsed = parse_utc("2026-07-26T12:00:00Z")

    assert parsed.tzinfo == timezone.utc
    assert parsed.hour == 12


def test_parse_utc_treats_naive_input_as_utc():
    parsed = parse_utc("2026-07-26T12:00:00")

    assert parsed.tzinfo == timezone.utc
    assert parsed.hour == 12


def test_parse_utc_converts_offset_to_utc():
    parsed = parse_utc("2026-07-26T23:30:00+05:00")

    assert parsed.tzinfo == timezone.utc
    assert parsed.hour == 18
    assert parsed.day == 26


def test_utc_day_bucket_basic():
    assert utc_day_bucket("2026-07-26T12:00:00Z") == "2026-07-26"


def test_utc_day_bucket_near_midnight_offset_rolls_to_next_utc_day():
    # 23:30 local at +05:00 is 18:30 UTC the same day — no rollover here,
    # but a positive local time close to midnight with a negative offset
    # rolls into the next UTC day.
    assert utc_day_bucket("2026-07-26T23:30:00-05:00") == "2026-07-27"


def test_utc_day_bucket_just_before_utc_midnight_stays_same_day():
    assert utc_day_bucket("2026-07-26T23:59:59Z") == "2026-07-26"
