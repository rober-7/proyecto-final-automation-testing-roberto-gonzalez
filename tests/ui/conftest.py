"""Fixtures propias de los tests de UI."""

import pytest

from pages import InventoryPage, LoginPage
from utils.data_reader import read_json

ESPERADOS = read_json("esperados.json")


@pytest.fixture
def inventory_page(driver):
    """Hace login con el usuario valido y devuelve la pagina de inventario ya cargada.

    Cada test que la usa arranca con su propia sesion, asi los tests
    son independientes entre si.
    """
    usuario = ESPERADOS["usuario_valido"]
    LoginPage(driver).load().login(usuario["username"], usuario["password"])
    return InventoryPage(driver).wait_until_loaded()
