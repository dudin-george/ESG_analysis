from datetime import datetime

from banki_ru.database import BankiRuBase
from banki_ru.insurance_parser import BankiInsurance
from banki_ru.queries import get_bank_list
from tests.mixins import TestMixin
import pytest


class TestBankiRuInsurance(TestMixin):
    @pytest.fixture
    def setup_test_reviews(self, mock_source, mock_get_source_by_id, mock_text, mock_insurance_list):
        return mock_source

    @pytest.fixture
    def setup_insurance_page_with_header(self, setup_test_reviews, mock_banki_ru_insurance_list, mock_insurance_page):
        BankiInsurance.get_pages_num_insurance_list = lambda x, y: 1
        yield setup_test_reviews

    def test_reviews(self, setup_insurance_page_with_header):
        broker_reviews = BankiInsurance()
        assert len(get_bank_list(broker_reviews.bank_site)) == 3

    def test_page_num(self, setup_insurance_page_with_header):
        broker_reviews = BankiInsurance()
        broker = BankiRuBase(id=1, bank_name="test", bank_id=1, bank_code=12345678)
        num = broker_reviews.get_pages_num(broker)
        assert num == 246  # check page num https://www.banki.ru/insurance/responses/company/alfastrahovanie/

    def test_page_reviews(self, setup_insurance_page_with_header):
        broker_reviews = BankiInsurance()
        broker = BankiRuBase(id=1, bank_name="test", bank_id=1, bank_code=12345678)
        reviews = broker_reviews.get_page_bank_reviews(broker, 1, datetime.fromtimestamp(1))
        assert len(reviews) == 25
