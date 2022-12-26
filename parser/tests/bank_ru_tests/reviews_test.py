from datetime import datetime

import pytest

from banki_ru.database import BankiRuBase
from banki_ru.reviews_parser import BankiReviews
from banki_ru.queries import get_bank_list
import requests_mock

from tests.mixins import TestMixin


class TestBankiRuReviews(TestMixin):
    @pytest.fixture
    def setup_test_reviews(self, api_source, api_bank, banki_banks_list):
        with requests_mock.Mocker() as m:
            m.post(api_source[0], status_code=200, json=api_source[1])
            m.get(api_bank[0], status_code=200, json=api_bank[1])
            m.get(banki_banks_list[0], status_code=200, json=banki_banks_list[1])
            yield m


    def test_reviews(self, setup_test_reviews): # todo licence id --- 1324-Л и тд
        banki_reviews = BankiReviews()
        assert len(get_bank_list(banki_reviews.bank_site)) == 2

    @pytest.fixture
    def setup_bank_page(self, setup_test_reviews, unicredit_reviews_response):
        m = setup_test_reviews
        m.get(unicredit_reviews_response[0], status_code=200, json=unicredit_reviews_response[1])
        yield

    def test_bank_page_num(self, setup_bank_page):
        banki_reviews = BankiReviews()
        bank = BankiRuBase(bank_id=1, bank_name="test", bank_code="unicreditbank")
        pages = banki_reviews.get_pages_num(bank)
        assert pages == 178

    def test_bank_page_reviews(self, setup_bank_page):
        banki_reviews = BankiReviews()
        bank = BankiRuBase(bank_id=1, bank_name="test", bank_code="unicreditbank")
        reviews = banki_reviews.get_page_bank_reviews(bank, page_num=1, parsed_time=datetime.fromtimestamp(1))
        assert len(reviews) == 2
