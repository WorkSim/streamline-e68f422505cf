"""Streamline — a nightly ETL pipeline modeled as pure, deterministic functions.

No database, no web framework, no clock, no network: the "target table" is a
plain list of dicts, timestamps are ISO-8601 strings, and every function is a
pure transformation of its inputs. This keeps the pipeline fully testable and
deterministic under pytest.
"""
