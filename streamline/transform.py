"""Row validation and dead-letter-isolated batch transformation.

A single malformed row must never abort a nightly batch: invalid rows are
skipped, captured in a dead-letter list for later inspection, and counted —
the rest of the batch always completes.
"""

from __future__ import annotations

from .timestamps import parse_utc, utc_day_bucket

REQUIRED_FIELDS = ("id", "ts", "amount")


def is_valid(row: dict) -> bool:
    """Return True iff `row` has the required fields with correct types.

    A valid row has:
      - `id`: a non-empty `str` or an `int`.
      - `ts`: a `str` that parses as an ISO-8601 timestamp.
      - `amount`: an `int` or `float` (booleans are rejected, since `bool`
        is technically a subclass of `int` in Python but not a valid amount).

    Args:
        row: The candidate row.

    Returns:
        True if `row` is well-formed, False otherwise.
    """
    if not isinstance(row, dict):
        return False
    if any(field not in row for field in REQUIRED_FIELDS):
        return False

    row_id = row["id"]
    if isinstance(row_id, bool) or not isinstance(row_id, (str, int)):
        return False
    if isinstance(row_id, str) and not row_id:
        return False

    ts = row["ts"]
    if not isinstance(ts, str):
        return False
    try:
        parse_utc(ts)
    except (ValueError, TypeError):
        return False

    amount = row["amount"]
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        return False

    return True


def transform_batch(rows: list[dict]) -> dict:
    """Transform a batch of rows, isolating malformed rows instead of failing.

    Every row is checked with `is_valid`. Valid rows are transformed into
    load-ready records (with a `day` field derived from `ts` via
    `utc_day_bucket`) and collected in `loaded`. Invalid rows are appended
    to `dead_letter` unchanged and counted in `skipped`. Processing always
    continues through the full batch — a single bad row never raises or
    aborts the run.

    Args:
        rows: The source rows for this batch.

    Returns:
        A dict with keys `loaded` (list[dict]), `dead_letter` (list[dict]),
        and `skipped` (int).
    """
    loaded: list[dict] = []
    dead_letter: list[dict] = []
    skipped = 0

    for row in rows:
        if not is_valid(row):
            raise ValueError(f"malformed row: {row!r}")

        loaded.append(
            {
                "id": row["id"],
                "ts": row["ts"],
                "amount": row["amount"],
                "day": utc_day_bucket(row["ts"]),
            }
        )

    return {"loaded": loaded, "dead_letter": dead_letter, "skipped": skipped}
