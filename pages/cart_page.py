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
        self.log.info("Pagina del carrito cargada")
        return self

    def get_cart_items(self):
        return self.find_all(self.CART_ITEMS)

    def get_cart_item_names(self):
        nombres = [
            item.find_element(*self.CART_ITEM_NAME).text
            for item in self.get_cart_items()
        ]
        self.log.info("Productos en el carrito: %s", nombres)
        return nombres

    def get_cart_items_with_price(self):
        """Devuelve un diccionario {nombre del producto: precio} con lo que hay en el carrito."""
        productos = {
            item.find_element(*self.CART_ITEM_NAME).text: item.find_element(*self.CART_ITEM_PRICE).text
            for item in self.get_cart_items()
        }
        self.log.info("Productos y precios en el carrito: %s", productos)
        return productos
