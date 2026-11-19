"""Tests de navegacion y verificacion del catalogo de productos."""

from utils.data_reader import read_json
from utils.logger import get_logger

ESPERADOS = read_json("esperados.json")

log = get_logger("tests.ui.catalogo")


class TestCatalogo:
    def test_titulo_de_pagina_de_inventario_es_correcto(self, inventory_page):
        assert inventory_page.get_page_title() == ESPERADOS["titulo_inventario"]

    def test_existen_productos_visibles_en_el_catalogo(self, inventory_page):
        assert len(inventory_page.get_products()) > 0

    def test_elementos_importantes_de_la_interfaz_estan_presentes(self, inventory_page):
        assert inventory_page.is_menu_present() is True
        assert inventory_page.is_sort_filter_present() is True

    def test_lista_nombre_y_precio_del_primer_producto(self, inventory_page):
        nombre, precio = inventory_page.get_first_product_name_and_price()

        assert nombre != ""
        assert precio.startswith("$")
        log.info("Primer producto encontrado -> Nombre: %s | Precio: %s", nombre, precio)
