"""Tests del flujo completo de compra (checkout) con los datos de data/checkout.json.

Flujo: login -> agregar productos -> carrito -> datos del comprador -> resumen -> confirmacion.
"""

from decimal import ROUND_HALF_UP, Decimal

import pytest

from pages import CartPage, CheckoutCompletePage, CheckoutInfoPage, CheckoutOverviewPage
from utils.data_reader import read_json

CHECKOUT = read_json("checkout.json")
FORMULARIOS_INCOMPLETOS = CHECKOUT["formularios_incompletos"]


def ir_al_formulario_del_comprador(driver, inventory_page, productos):
    """Agrega los productos al carrito y avanza hasta el formulario de datos del comprador."""
    for nombre in productos:
        inventory_page.add_product_to_cart(nombre)
    inventory_page.go_to_cart()
    CartPage(driver).wait_until_loaded().go_to_checkout()
    return CheckoutInfoPage(driver).wait_until_loaded()


class TestCheckout:
    def test_compra_completa_de_punta_a_punta(self, driver, inventory_page):
        comprador = CHECKOUT["comprador"]
        info_page = ir_al_formulario_del_comprador(driver, inventory_page, CHECKOUT["productos"])

        info_page.fill_buyer_info(comprador["nombre"], comprador["apellido"], comprador["codigo_postal"])
        info_page.click_continue()

        overview_page = CheckoutOverviewPage(driver).wait_until_loaded()
        assert len(overview_page.get_item_prices()) == len(CHECKOUT["productos"])

        overview_page.finish_purchase()

        complete_page = CheckoutCompletePage(driver).wait_until_loaded()
        assert complete_page.get_confirmation_message() == CHECKOUT["mensaje_confirmacion"]
        assert complete_page.is_back_home_button_visible() is True

    def test_resumen_calcula_subtotal_impuestos_y_total(self, driver, inventory_page):
        comprador = CHECKOUT["comprador"]
        info_page = ir_al_formulario_del_comprador(driver, inventory_page, CHECKOUT["productos"])
        info_page.fill_buyer_info(comprador["nombre"], comprador["apellido"], comprador["codigo_postal"])
        info_page.click_continue()

        overview_page = CheckoutOverviewPage(driver).wait_until_loaded()
        subtotal = overview_page.get_subtotal()
        impuesto = overview_page.get_tax()
        impuesto_esperado = (subtotal * Decimal(CHECKOUT["tasa_impuesto"])).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        assert subtotal == sum(overview_page.get_item_prices())
        assert impuesto == impuesto_esperado
        assert overview_page.get_total() == subtotal + impuesto

    @pytest.mark.parametrize("formulario", FORMULARIOS_INCOMPLETOS, ids=[f["caso"] for f in FORMULARIOS_INCOMPLETOS])
    def test_formulario_incompleto_muestra_mensaje_de_error(self, driver, inventory_page, formulario):
        info_page = ir_al_formulario_del_comprador(driver, inventory_page, CHECKOUT["productos"][:1])

        info_page.fill_buyer_info(formulario["nombre"], formulario["apellido"], formulario["codigo_postal"])
        info_page.click_continue()

        assert info_page.get_error_message() == formulario["mensaje_error"]
        assert "/checkout-step-one.html" in driver.current_url
