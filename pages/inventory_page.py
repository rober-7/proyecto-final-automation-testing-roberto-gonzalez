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
        cantidad_previa = self._current_cart_count()
        self.click(self.FIRST_ADD_TO_CART_BUTTON)
        self._wait_for_cart_count(cantidad_previa + 1)

    def add_product_to_cart(self, nombre_producto):
        """Busca el producto por su nombre en el catalogo y clickea su boton 'Add to cart'."""
        self.log.info("Agregando al carrito: '%s'", nombre_producto)
        for producto in self.get_products():
            if producto.find_element(*self.PRODUCT_NAME).text == nombre_producto:
                cantidad_previa = self._current_cart_count()
                producto.find_element(*self.PRODUCT_BUTTON).click()
                self._wait_for_cart_count(cantidad_previa + 1)
                return
        raise ValueError(f"El producto '{nombre_producto}' no existe en el catalogo")

    def _current_cart_count(self):
        """Cantidad que muestra el contador del carrito (0 si el contador no esta visible)."""
        badges = self.driver.find_elements(*self.CART_BADGE)
        return int(badges[0].text) if badges else 0

    def _wait_for_cart_count(self, cantidad):
        """Espera a que el sitio termine de registrar el producto antes de seguir.

        Sin esta espera, navegar enseguida al carrito puede perder el click o
        mostrar el carrito vacio (condicion de carrera con la actualizacion de la pagina).
        """
        self.log.debug("Esperando que el contador del carrito llegue a %d", cantidad)
        self.wait.until(lambda driver: self._current_cart_count() == cantidad)

    def get_cart_badge_count(self):
        cantidad = int(self.get_text(self.CART_BADGE))
        self.log.info("Contador del carrito: %d", cantidad)
        return cantidad

    def go_to_cart(self):
        self.log.info("Navegando al carrito")
        self.click(self.CART_LINK)
