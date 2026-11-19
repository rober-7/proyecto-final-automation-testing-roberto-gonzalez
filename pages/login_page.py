"""Page Object de la pagina de login de saucedemo.com."""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    # Localizadores
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def load(self):
        self.open()
        self.find(self.USERNAME_INPUT)
        return self

    def login(self, username, password):
        self.log.info("Iniciando sesion con usuario '%s'", username)
        self.type(self.USERNAME_INPUT, username)
        self.type(self.PASSWORD_INPUT, password, sensitive=True)
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self):
        mensaje = self.get_text(self.ERROR_MESSAGE)
        self.log.info("Mensaje de error mostrado: '%s'", mensaje)
        return mensaje
