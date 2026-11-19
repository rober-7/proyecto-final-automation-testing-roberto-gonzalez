"""Page Object de la pagina de inventario (catalogo de productos)."""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class InventoryPage(BasePage):
    # Localizadores
    PAGE_TITLE = (By.CLASS_NAME, "title")
    INVENTORY_CONTAINER = (By.ID, "inventory_container")
    PRODUCT_ITEMS = (By.CLASS_NAME, "inventory_item")
    PRODUCT_NAME = (By.CLASS_NAME, "inventory_item_name")
    PRODUCT_PRICE = (By.CLASS_NAME, "inventory_item_price")
    PRODUCT_BUTTON = (By.TAG_NAME, "button")
    FIRST_ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, ".inventory_item button")
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    PRODUCT_SORT_FILTER = (By.CLASS_NAME, "product_sort_container")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")

    def wait_until_loaded(self):
        self.wait_for_url("/inventory.html")
        self.find(self.INVENTORY_CONTAINER)
        self.log.info("Pagina de inventario cargada")
        return self

    def get_page_title(self):
        return self.get_text(self.PAGE_TITLE)

    def get_products(self):
        return self.find_all(self.PRODUCT_ITEMS)

    def is_menu_present(self):
        return self.is_visible(self.MENU_BUTTON)

    def is_sort_filter_present(self):
        return self.is_visible(self.PRODUCT_SORT_FILTER)

    def get_first_product_name_and_price(self):
        primer_producto = self.get_products()[0]
        nombre = primer_producto.find_element(*self.PRODUCT_NAME).text
        precio = primer_producto.find_element(*self.PRODUCT_PRICE).text
        self.log.info("Primer producto del catalogo: '%s' (%s)", nombre, precio)
        return nombre, precio

    def add_first_product_to_cart(self):
        self.log.info("Agregando el primer producto al carrito")
        self.click(self.FIRST_ADD_TO_CART_BUTTON)

    def add_product_to_cart(self, nombre_producto):
        """Busca el producto por su nombre en el catalogo y clickea su boton 'Add to cart'."""
        self.log.info("Agregando al carrito: '%s'", nombre_producto)
        for producto in self.get_products():
            if producto.find_element(*self.PRODUCT_NAME).text == nombre_producto:
                producto.find_element(*self.PRODUCT_BUTTON).click()
                return
        raise ValueError(f"El producto '{nombre_producto}' no existe en el catalogo")

    def get_cart_badge_count(self):
        cantidad = int(self.get_text(self.CART_BADGE))
        self.log.info("Contador del carrito: %d", cantidad)
        return cantidad

    def go_to_cart(self):
        self.log.info("Navegando al carrito")
        self.click(self.CART_LINK)
