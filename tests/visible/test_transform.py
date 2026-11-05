"""Visible tests for streamline.transform — develop against these."""

from streamline.transform import is_valid, transform_batch


def test_is_valid_accepts_well_formed_row():
    assert is_valid({"id": 1, "ts": "2026-07-26T12:00:00Z", "amount": 10.5}) is True


def test_is_valid_rejects_missing_field():
    assert is_valid({"id": 1, "ts": "2026-07-26T12:00:00Z"}) is False


def test_is_valid_rejects_bad_timestamp():
    assert is_valid({"id": 1, "ts": "not-a-timestamp", "amount": 10}) is False


def test_is_valid_rejects_non_numeric_amount():
    assert is_valid({"id": 1, "ts": "2026-07-26T12:00:00Z", "amount": "10"}) is False


def test_transform_batch_isolates_bad_row_and_completes():
    rows = [
        {"id": 1, "ts": "2026-07-26T12:00:00Z", "amount": 10},
        {"id": 2, "ts": "bad-timestamp", "amount": 20},
        {"id": 3, "ts": "2026-07-26T13:00:00Z", "amount": 30},
    ]

    result = transform_batch(rows)

    assert [row["id"] for row in result["loaded"]] == [1, 3]
    assert result["dead_letter"] == [{"id": 2, "ts": "bad-timestamp", "amount": 20}]
    assert result["skipped"] == 1


def test_transform_batch_reports_zero_skipped_when_all_valid():
    rows = [
        {"id": 1, "ts": "2026-07-26T12:00:00Z", "amount": 10},
        {"id": 2, "ts": "2026-07-26T13:00:00Z", "amount": 20},
    ]

    result = transform_batch(rows)

    assert result["skipped"] == 0
    assert len(result["loaded"]) == 2
    assert result["dead_letter"] == []


def test_transform_batch_never_raises_on_multiple_bad_rows():
    rows = [
        {"id": 1, "ts": "2026-07-26T12:00:00Z", "amount": 10},
        {"amount": 20},
        {"id": 3, "ts": "2026-07-26T13:00:00Z", "amount": "not-a-number"},
    ]

    result = transform_batch(rows)

    assert result["skipped"] == 2
    assert len(result["loaded"]) == 1
