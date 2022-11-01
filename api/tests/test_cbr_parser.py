import os

import pytest

from app.bank_parser import CBRParser
from app.query.bank import get_bank_count

TEST_REAL_PAGE = os.getenv("TEST_REAL_PAGE", "False").lower() == "true"


class TestCBRParser:
    @pytest.fixture(autouse=True)
    def get_cbr_page(self, session, cbr_page):
        self.session = session
        self.cbr_page = cbr_page
        self.cbr = CBRParser(self.session)
        self.cbr.get_page = lambda: self.cbr_page

    async def test_get_page(self, migrated_postgres):
        await self.cbr.load_banks()
        assert await get_bank_count(self.session) > 300

    def test_bank_list(self, migrated_postgres):
        banks = self.cbr.get_bank_list(self.cbr_page)
        assert len(banks) > 300
