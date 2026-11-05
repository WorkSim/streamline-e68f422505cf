# Streamline

Streamline is a minimal Python ETL pipeline used as a **debugging sandbox** within the WorkSim platform. It models a nightly ETL job — load, timestamp bucketing, and per-row transformation — as pure, deterministic functions, with intentional, documented bugs planted for candidate learning and assessment.

## Overview

**What it is:** A lightweight, dependency-free Python package with:
- Idempotent upsert-style loading into an in-memory "target table"
- UTC-correct timestamp parsing and day bucketing
- Per-row error isolation during batch transformation (dead-letter, not fatal)
- Intentional seeded bugs (via patches) that candidates must fix

**What it's for:** WorkSim uses Streamline to test data-engineering problem-solving skills — idempotency, timezone correctness, and fault isolation — the kind of bugs that show up in real nightly-batch pipelines.

**Key constraint:** This is a standalone template repo. `main` here is the correct, unmodified baseline implementation. At provision time, the platform plants every bug in the sprint into a student's own copy of the repo's root commit — so while this template's `main` stays clean, a student's `main` carries all of the sprint's known defects from the start. The assigned ticket names the one in scope; unrelated failures are other tickets' bugs, not something to fix. There is no database, web framework, clock, or network call anywhere in the app — every function is a pure transformation of its inputs, so pytest runs are fully deterministic.

## Quick Start

### Prerequisites
- Python 3.13+
- pip

### Installation & Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests (visible + grading)
python3 -m pytest tests -q

# Run only the visible tests
python3 -m pytest tests/visible -q

# Run only the grading tests (authoritative test suite)
python3 -m pytest tests/grading -q
```

## Project Structure

```
streamline/
├── streamline/
│   ├── __init__.py
│   ├── load.py            # upsert_rows() — idempotent load by natural key
│   ├── timestamps.py      # parse_utc(), utc_day_bucket() — UTC-correct parsing
│   └── transform.py       # is_valid(), transform_batch() — dead-letter isolation
├── tests/
│   ├── visible/            # VISIBLE tests (develop against these)
│   │   ├── test_load.py
│   │   ├── test_timestamps.py
│   │   └── test_transform.py
│   └── grading/             # GRADING tests (restored from baseline in CI)
│       ├── test_idempotent_load.py
│       ├── test_utc_bucketing.py
│       └── test_malformed_row_isolation.py
├── .github/workflows/
│   └── grade.yml             # CI grading workflow
├── requirements.txt
├── pytest.ini
└── .gitignore
```

## Testing Strategy

Streamline uses a **two-tier test split** for learning and assessment:

### Visible Tests (`tests/visible/`)
- **Purpose:** For candidates to develop and validate their fixes
- **Run:** `python3 -m pytest tests/visible -q`
- **Edit:** Safe to edit and experiment with

### Grading Tests (`tests/grading/`)
- **Purpose:** Authoritative test suite for final assessment
- **Run:** `python3 -m pytest tests/grading -q`
- **Edit:** Do not edit — these are restored from the baseline in CI
- **Coverage:** One module per seeded bug
  - `test_idempotent_load.py` — DATA-501 (upsert correctness)
  - `test_utc_bucketing.py` — DATA-509 (UTC parsing + day bucketing)
  - `test_malformed_row_isolation.py` — DATA-514 (dead-letter isolation)

**Important:** This template repo's own `main` is the correct baseline. A student's provisioned repo ships with the sprint's known defects already committed to `main`; the assigned ticket names the one in scope. Running `python3 -m pytest tests -q` in a student's repo may show unrelated failures — those are other tickets' bugs, not something to fix.

## CI Grading Workflow

The `.github/workflows/grade.yml` workflow runs on every pull request targeting `main`:

1. Checks out the PR's merge ref (candidate code + grading baseline merged)
2. Restores `tests/grading`, `requirements.txt`, and `.github/grading-map.json` from the base branch — so a PR cannot fake a pass by editing those files
3. **Scopes the run to the ticket the PR is for**, then installs with `pip install -r requirements.txt` and runs `python -m pytest tests/grading -q`

### Why scoping matters

Every one of the sprint's bugs is planted in your repo's root commit from day one. An
unscoped run therefore fails on the tickets you have not been assigned yet, so a
perfectly correct day-1 PR would show a red check. That is noise, not signal.

The workflow finds the ticket id in your **branch name**, then the **PR title**, then the
**PR body** — first match wins — and removes the other tickets' grading files before
running. Name your branch after the ticket and the check grades only your work:

```
git checkout -b data-501-short-description
```

If no ticket id is found anywhere, the workflow runs everything and says so in the job
summary rather than pretending the result is meaningful.

## Development Tips

### Understanding the Modules

- `streamline/load.py` — `upsert_rows(table, new_rows, key="id")` returns a **new** table (never mutates inputs) where each new row replaces any existing row sharing its key, and is appended otherwise.
- `streamline/timestamps.py` — `parse_utc(ts)` always returns a tz-aware UTC `datetime`, treating naive input as already UTC (never host-local). `utc_day_bucket(ts)` returns the `YYYY-MM-DD` UTC date.
- `streamline/transform.py` — `is_valid(row)` checks the required fields/types; `transform_batch(rows)` never raises on a bad row — it isolates it into `dead_letter`, increments `skipped`, and keeps processing the rest of the batch.

### Running Tests Locally

```bash
# All tests
python3 -m pytest tests -q

# Verbose
python3 -m pytest tests -v

# One module
python3 -m pytest tests/visible/test_load.py -q
```

## Troubleshooting

**Q: Tests fail on `main`?**
A: Expected. Your repo ships with the sprint's known defects; your ticket names the one in scope. Unrelated failures are other tickets' bugs, not something to revert.

**Q: Grading tests are passing but I expected them to fail?**
A: All the sprint's known defects are already committed on `main` when your repo is provisioned; this template's own `main` is the correct baseline. Your ticket names the one in scope for grading.

**Q: Can I edit the grading tests?**
A: Not in the template. CI always restores them from the baseline. Edits in your fork are local only; the authoritative grading happens against the restored tests.

## Environment Variables

Streamline uses no external APIs, database, or environment variables. All data flows through the pipeline in-memory (see `tests/` for example row shapes), keeping the pipeline fully deterministic.

---

**Maintained By:** WorkSim Team
