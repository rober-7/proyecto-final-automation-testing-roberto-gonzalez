"""Tests del carrito de compras.

El test parametrizado agrega cada producto de data/productos.json y
verifica que aparezca en el carrito con el precio correcto.
"""

import pytest

from pages import CartPage
from utils.data_reader import read_json

PRODUCTOS = read_json("productos.json")


class TestCarrito:
    def test_agregar_producto_incrementa_contador_del_carrito(self, inventory_page):
        inventory_page.add_first_product_to_cart()

        assert inventory_page.get_cart_badge_count() == 1

    @pytest.mark.parametrize("producto", PRODUCTOS, ids=[p["nombre"] for p in PRODUCTOS])
    def test_producto_agregado_aparece_en_el_carrito_con_su_precio(self, driver, inventory_page, producto):
        inventory_page.add_product_to_cart(producto["nombre"])
        inventory_page.go_to_cart()

        productos_en_carrito = CartPage(driver).wait_until_loaded().get_cart_items_with_price()

        assert productos_en_carrito == {producto["nombre"]: producto["precio"]}
