"""Page Object del paso 1 del checkout: formulario con los datos del comprador."""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutInfoPage(BasePage):
    # Localizadores
    FIRST_NAME_INPUT = (By.ID, "first-name")
    LAST_NAME_INPUT = (By.ID, "last-name")
    POSTAL_CODE_INPUT = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def wait_until_loaded(self):
        self.wait_for_url("/checkout-step-one.html")
        self.log.info("Formulario de datos del comprador cargado")
        return self

    def fill_buyer_info(self, nombre, apellido, codigo_postal):
        self.log.info("Completando datos del comprador: '%s' '%s' (CP: '%s')", nombre, apellido, codigo_postal)
        self.type(self.FIRST_NAME_INPUT, nombre)
        self.type(self.LAST_NAME_INPUT, apellido)
        self.type(self.POSTAL_CODE_INPUT, codigo_postal)

    def click_continue(self):
        self.log.info("Enviando el formulario del comprador")
        self.click(self.CONTINUE_BUTTON)

    def get_error_message(self):
        mensaje = self.get_text(self.ERROR_MESSAGE)
        self.log.info("Mensaje de error mostrado: '%s'", mensaje)
        return mensaje
