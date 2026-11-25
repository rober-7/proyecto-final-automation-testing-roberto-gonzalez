"""Page Object del paso final del checkout: confirmacion de la compra."""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutCompletePage(BasePage):
    # Localizadores
    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")
    BACK_HOME_BUTTON = (By.ID, "back-to-products")

    def wait_until_loaded(self):
        self.wait_for_url("/checkout-complete.html")
        self.log.info("Pagina de compra completada cargada")
        return self

    def get_confirmation_message(self):
        mensaje = self.get_text(self.COMPLETE_HEADER)
        self.log.info("Mensaje de confirmacion: '%s'", mensaje)
        return mensaje

    def is_back_home_button_visible(self):
        return self.is_visible(self.BACK_HOME_BUTTON)
