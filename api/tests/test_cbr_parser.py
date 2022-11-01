import os

import pytest

from app.bank_parser import CBRParser
from app.query.bank import get_bank_count

TEST_REAL_PAGE = os.getenv("TEST_REAL_PAGE", "False").lower() == "true"


@pytest.mark.skipif(not TEST_REAL_PAGE, reason="ddos cbr")
async def test_get_real_page(session):
    await CBRParser(session).load_banks()
    assert await get_bank_count(session) > 300


""
async def test_get_page(session, cbr_page, migrated_postgres):
    cbr = CBRParser(session)
    cbr.get_page = lambda: cbr_page
    await cbr.load_banks()
    assert await get_bank_count(session) > 300


""
def test_bank_list(session, cbr_page, migrated_postgres):
    cbr = CBRParser(session)
    banks = cbr.get_bank_list(cbr_page)
    assert len(banks) > 300
