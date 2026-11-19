"""Tests de login parametrizados con los usuarios de data/usuarios_login.csv.

Cada fila del CSV se convierte en un caso de prueba independiente. Para
agregar un caso nuevo alcanza con sumar una fila al archivo.
"""

import pytest

from pages import InventoryPage, LoginPage
from utils.data_reader import read_csv, read_json

USUARIOS = read_csv("usuarios_login.csv")
ESPERADOS = read_json("esperados.json")


def casos_con_resultado(resultado):
    """Filtra las filas del CSV por resultado esperado y usa la columna 'caso' como nombre del test."""
    return [
        pytest.param(fila, id=fila["caso"])
        for fila in USUARIOS
        if fila["resultado_esperado"] == resultado
    ]


class TestLogin:
    @pytest.mark.parametrize("usuario", casos_con_resultado("exito"))
    def test_login_exitoso_redirige_al_inventario(self, driver, usuario):
        LoginPage(driver).load().login(usuario["username"], usuario["password"])
        inventory_page = InventoryPage(driver).wait_until_loaded()

        assert "/inventory.html" in driver.current_url
        assert driver.title == ESPERADOS["titulo_pestana"]
        assert inventory_page.get_page_title() == ESPERADOS["titulo_inventario"]

    @pytest.mark.parametrize("usuario", casos_con_resultado("error"))
    def test_login_fallido_muestra_mensaje_de_error(self, driver, usuario):
        login_page = LoginPage(driver).load()
        login_page.login(usuario["username"], usuario["password"])

        assert login_page.get_error_message() == usuario["mensaje_error"]
        assert "/inventory.html" not in driver.current_url
