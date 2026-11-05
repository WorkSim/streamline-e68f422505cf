"""Grading suite for DATA-501 — idempotent load (upsert on natural key).

Acceptance criteria:
  - Re-running a load for the same source batch yields an identical table
    (no duplicates, no drift in totals).
  - A partial re-run (a subset of rows, some changed) reconciles: matching
    rows are replaced, not duplicated.
  - Rows for other keys (e.g. other dates/entities) are left untouched.
"""

from streamline.load import upsert_rows


def _totals(table: list[dict]) -> float:
    return sum(row["amount"] for row in table)


def test_rerun_same_batch_yields_identical_table_and_totals():
    table: list[dict] = []
    batch = [
        {"id": "2026-07-26#1", "amount": 100},
        {"id": "2026-07-26#2", "amount": 250},
        {"id": "2026-07-26#3", "amount": 75},
    ]

    first_run = upsert_rows(table, batch)
    second_run = upsert_rows(first_run, batch)

    assert second_run == first_run
    assert len(second_run) == 3
    assert _totals(second_run) == _totals(first_run) == 425


def test_rerun_no_duplicate_rows_for_same_key():
    table = [{"id": "A", "amount": 10}]
    # Simulate re-running the *same* source row across three nightly runs.
    for _ in range(3):
        table = upsert_rows(table, [{"id": "A", "amount": 10}])

    assert table == [{"id": "A", "amount": 10}]


def test_partial_rerun_reconciles_changed_rows_without_duplicating():
    table = upsert_rows(
        [],
        [
            {"id": "A", "amount": 10},
            {"id": "B", "amount": 20},
            {"id": "C", "amount": 30},
        ],
    )

    # A correction batch only re-sends A (corrected) and a brand-new row D.
    reconciled = upsert_rows(table, [{"id": "A", "amount": 15}, {"id": "D", "amount": 40}])

    assert len(reconciled) == 4
    by_id = {row["id"]: row["amount"] for row in reconciled}
    assert by_id == {"A": 15, "B": 20, "C": 30, "D": 40}


def test_upsert_does_not_disturb_rows_for_other_keys():
    table = upsert_rows(
        [],
        [
            {"id": "2026-07-25#1", "amount": 500},
            {"id": "2026-07-26#1", "amount": 100},
        ],
    )

    # Only touch 2026-07-26's row; 2026-07-25's row must be untouched.
    updated = upsert_rows(table, [{"id": "2026-07-26#1", "amount": 999}])

    day_25_row = next(row for row in updated if row["id"] == "2026-07-25#1")
    assert day_25_row == {"id": "2026-07-25#1", "amount": 500}


def test_upsert_preserves_row_order_for_untouched_rows():
    table = upsert_rows(
        [],
        [{"id": 1, "amount": 1}, {"id": 2, "amount": 2}, {"id": 3, "amount": 3}],
    )

    updated = upsert_rows(table, [{"id": 2, "amount": 20}])

    assert [row["id"] for row in updated] == [1, 2, 3]
    assert updated[1]["amount"] == 20
