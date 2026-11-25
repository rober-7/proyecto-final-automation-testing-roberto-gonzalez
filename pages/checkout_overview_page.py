"""Page Object del paso 2 del checkout: resumen con productos, impuestos y total."""

from decimal import Decimal

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


def parse_price(texto):
    """Extrae el importe de textos como '$29.99' o 'Item total: $39.98' y lo devuelve como Decimal."""
    return Decimal(texto.split("$")[-1])


class CheckoutOverviewPage(BasePage):
    # Localizadores
    ITEM_PRICES = (By.CLASS_NAME, "inventory_item_price")
    SUBTOTAL_LABEL = (By.CLASS_NAME, "summary_subtotal_label")
    TAX_LABEL = (By.CLASS_NAME, "summary_tax_label")
    TOTAL_LABEL = (By.CLASS_NAME, "summary_total_label")
    FINISH_BUTTON = (By.ID, "finish")

    def wait_until_loaded(self):
        self.wait_for_url("/checkout-step-two.html")
        self.log.info("Resumen de la compra cargado")
        return self

    def get_item_prices(self):
        return [parse_price(precio.text) for precio in self.find_all(self.ITEM_PRICES)]

    def get_subtotal(self):
        return parse_price(self.get_text(self.SUBTOTAL_LABEL))

    def get_tax(self):
        return parse_price(self.get_text(self.TAX_LABEL))

    def get_total(self):
        total = parse_price(self.get_text(self.TOTAL_LABEL))
        self.log.info("Total de la compra: $%s", total)
        return total

    def finish_purchase(self):
        self.log.info("Confirmando la compra")
        self.click(self.FINISH_BUTTON)
