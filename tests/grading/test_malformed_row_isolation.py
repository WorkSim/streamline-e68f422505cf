"""Grading suite for DATA-514 — per-row error isolation in batch transform.

Acceptance criteria:
  - A malformed row is skipped and sent to a dead-letter sink, never
    fatal to the batch.
  - The batch always completes, even with multiple bad rows, or when
    every row is bad, or when a bad row is the very last one processed.
  - The run summary reports an accurate skipped-row count.
"""

from streamline.transform import transform_batch


def test_single_malformed_row_is_isolated_not_fatal():
    rows = [
        {"id": 1, "ts": "2026-07-26T12:00:00Z", "amount": 10},
        {"id": 2, "ts": "2026-07-26T13:00:00Z", "amount": "not-a-number"},
        {"id": 3, "ts": "2026-07-26T14:00:00Z", "amount": 30},
    ]

    result = transform_batch(rows)

    assert [row["id"] for row in result["loaded"]] == [1, 3]
    assert [row["id"] for row in result["dead_letter"]] == [2]
    assert result["skipped"] == 1


def test_batch_completes_when_every_row_is_malformed():
    rows = [
        {"id": 1, "amount": 10},  # missing ts
        {"ts": "2026-07-26T12:00:00Z", "amount": 10},  # missing id
        {"id": 3, "ts": "2026-07-26T12:00:00Z", "amount": "bad"},  # bad amount type
    ]

    result = transform_batch(rows)

    assert result["loaded"] == []
    assert len(result["dead_letter"]) == 3
    assert result["skipped"] == 3


def test_batch_completes_when_bad_row_is_last():
    rows = [
        {"id": 1, "ts": "2026-07-26T12:00:00Z", "amount": 10},
        {"id": 2, "ts": "2026-07-26T13:00:00Z", "amount": 20},
        {"id": 3, "ts": "not-a-valid-timestamp", "amount": 30},
    ]

    result = transform_batch(rows)

    assert len(result["loaded"]) == 2
    assert result["skipped"] == 1
    assert result["dead_letter"][0]["id"] == 3


def test_skipped_count_matches_dead_letter_length_exactly():
    rows = [
        {"id": 1, "ts": "2026-07-26T12:00:00Z", "amount": 10},
        {"id": 2, "amount": 20},
        {"id": 3, "ts": "2026-07-26T13:00:00Z"},
        {"id": 4, "ts": "2026-07-26T14:00:00Z", "amount": 40},
        {"id": 5, "ts": "bad", "amount": 50},
    ]

    result = transform_batch(rows)

    assert result["skipped"] == len(result["dead_letter"]) == 3
    assert len(result["loaded"]) == 2


def test_dead_letter_rows_are_preserved_unmodified():
    bad_row = {"id": 1, "ts": "2026-07-26T12:00:00Z", "amount": None}

    result = transform_batch([bad_row])

    assert result["dead_letter"] == [bad_row]


def test_empty_batch_completes_with_zero_skipped():
    result = transform_batch([])

    assert result == {"loaded": [], "dead_letter": [], "skipped": 0}
