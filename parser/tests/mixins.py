import pytest


class TestMixin:
    @pytest.fixture(autouse=True, scope="function")
    def setup(self, session, mocker):
        self.session = session
        mocker.patch("common.base_parser.sleep", return_value=None)
