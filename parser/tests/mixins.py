import pytest

class TestMixin:
    @pytest.fixture(autouse=True, scope="function")
    def setup(self, session):
        self.session = session
