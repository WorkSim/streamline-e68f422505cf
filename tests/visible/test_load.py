"""Visible tests for streamline.load — develop against these."""

from streamline.load import upsert_rows


def test_upsert_replaces_existing_row_by_key():
    table = [{"id": 1, "amount": 10}, {"id": 2, "amount": 20}]
    new_rows = [{"id": 1, "amount": 99}]

    result = upsert_rows(table, new_rows)

    assert result == [{"id": 1, "amount": 99}, {"id": 2, "amount": 20}]


def test_upsert_appends_new_rows():
    table = [{"id": 1, "amount": 10}]
    new_rows = [{"id": 2, "amount": 20}]

    result = upsert_rows(table, new_rows)

    assert result == [{"id": 1, "amount": 10}, {"id": 2, "amount": 20}]


def test_upsert_leaves_untouched_rows_alone():
    table = [{"id": 1, "amount": 10}, {"id": 2, "amount": 20}, {"id": 3, "amount": 30}]
    new_rows = [{"id": 2, "amount": 200}]

    result = upsert_rows(table, new_rows)

    assert result[0] == {"id": 1, "amount": 10}
    assert result[2] == {"id": 3, "amount": 30}


def test_upsert_rerun_is_idempotent():
    table: list[dict] = []
    batch = [{"id": 1, "amount": 10}, {"id": 2, "amount": 20}]

    first = upsert_rows(table, batch)
    second = upsert_rows(first, batch)

    assert first == second


def test_upsert_does_not_mutate_inputs():
    table = [{"id": 1, "amount": 10}]
    new_rows = [{"id": 1, "amount": 99}]

    upsert_rows(table, new_rows)

    assert table == [{"id": 1, "amount": 10}]


def test_upsert_supports_custom_key():
    table = [{"sku": "A", "qty": 1}]
    new_rows = [{"sku": "A", "qty": 5}, {"sku": "B", "qty": 2}]

    result = upsert_rows(table, new_rows, key="sku")

    assert result == [{"sku": "A", "qty": 5}, {"sku": "B", "qty": 2}]
