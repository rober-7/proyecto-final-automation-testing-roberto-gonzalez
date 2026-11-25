"""Fixtures propias de los tests de API."""

import pytest

from utils.api_client import ApiClient
from utils.data_reader import read_json


@pytest.fixture(scope="session")
def api_data():
    return read_json("api.json")


@pytest.fixture
def api_client(api_data):
    """Cliente HTTP nuevo para cada test (sin estado compartido entre tests)."""
    cliente = ApiClient(api_data["base_url"])
    yield cliente
    cliente.close()
