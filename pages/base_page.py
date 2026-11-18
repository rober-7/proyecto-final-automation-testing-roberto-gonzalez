"""Clase base de todos los Page Objects.

Centraliza el driver, las esperas explicitas (WebDriverWait) y las acciones
comunes (buscar, clickear, escribir, leer texto) para que cada pagina concreta
solo tenga que declarar sus localizadores y sus acciones de negocio.
"""

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://www.saucedemo.com/"
DEFAULT_TIMEOUT = 10


class BasePage:
    def __init__(self, driver, timeout=DEFAULT_TIMEOUT):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, path=""):
        self.driver.get(BASE_URL + path)

    def find(self, locator):
        """Espera a que el elemento sea visible y lo devuelve."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text):
        elemento = self.find(locator)
        elemento.clear()
        elemento.send_keys(text)

    def get_text(self, locator):
        return self.find(locator).text

    def is_visible(self, locator):
        return self.find(locator).is_displayed()

    def wait_for_url(self, fragment):
        self.wait.until(EC.url_contains(fragment))
