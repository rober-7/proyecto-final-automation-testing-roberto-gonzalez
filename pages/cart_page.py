"""Page Object de la pagina del carrito de compras."""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CartPage(BasePage):
    # Localizadores
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    CART_ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    CART_ITEM_PRICE = (By.CLASS_NAME, "inventory_item_price")

    def wait_until_loaded(self):
        self.wait_for_url("/cart.html")
        return self

    def get_cart_items(self):
        return self.find_all(self.CART_ITEMS)

    def get_cart_item_names(self):
        return [
            item.find_element(*self.CART_ITEM_NAME).text
            for item in self.get_cart_items()
        ]
