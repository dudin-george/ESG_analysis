import pytest

from app.bank_parser import CBRParser
from app.query.bank import get_bank_count
import os

TEST_REAL_PAGE = os.getenv("TEST_REAL_PAGE", "False").lower() == "true"


@pytest.mark.skipif(not TEST_REAL_PAGE, reason="ddos cbr")
def test_get_real_page(session):
    CBRParser(session).load_banks()
    with session as db:
        assert get_bank_count(db) > 300


def test_get_page(session, cbr_page):
    cbr = CBRParser(session)
    cbr.get_page = lambda: cbr_page
    with session as db:
        cbr.load_banks()
        assert get_bank_count(db) > 300


def test_bank_list(session, cbr_page):
    cbr = CBRParser(session)
    banks = cbr.get_bank_list(cbr_page)
    assert len(banks) > 300
