from datetime import date

from collectors.valorant.ingest import parse_match_date


def test_parse_iso_date():
    assert parse_match_date({"date": "2025-03-14"}) == date(2025, 3, 14)


def test_parse_vlr_timestamp_when_human_date_is_unparseable():
    assert parse_match_date({
        "date": "Mar 14, 2025",
        "unix_timestamp": "2025-03-14 18:30:00",
    }) == date(2025, 3, 14)


def test_parse_long_month_date():
    assert parse_match_date({"date": "March 14, 2025"}) == date(2025, 3, 14)


def test_unknown_date_is_not_guessed():
    assert parse_match_date({"date": "TBD"}) is None
