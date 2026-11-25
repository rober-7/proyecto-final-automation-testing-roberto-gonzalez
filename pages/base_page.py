"""Clase base de todos los Page Objects.

Centraliza el driver, las esperas explicitas (WebDriverWait) y las acciones
comunes (buscar, clickear, escribir, leer texto) para que cada pagina concreta
solo tenga que declarar sus localizadores y sus acciones de negocio.

Cada accion queda registrada en el log: en nivel DEBUG las acciones sobre
elementos (click, escribir) y en nivel INFO las acciones de negocio que
definen las paginas hijas (login, agregar al carrito, etc.).
"""

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.logger import get_logger

BASE_URL = "https://www.saucedemo.com/"
DEFAULT_TIMEOUT = 10


def describe(locator):
    """Convierte un localizador (By.ID, "user-name") en texto legible: id=user-name."""
    by, value = locator
    return f"{by}={value}"


class BasePage:
    def __init__(self, driver, timeout=DEFAULT_TIMEOUT):
        self.driver = driver
        # Se ignoran los elementos "stale" (re-dibujados por la pagina) mientras se espera
        self.wait = WebDriverWait(driver, timeout, ignored_exceptions=(StaleElementReferenceException,))
        self.log = get_logger(f"pages.{type(self).__name__}")

    def open(self, path=""):
        url = BASE_URL + path
        self.log.info("Abriendo URL: %s", url)
        self.driver.get(url)

    def find(self, locator):
        """Espera a que el elemento sea visible y lo devuelve."""
        self.log.debug("Esperando elemento visible: %s", describe(locator))
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator):
        elementos = self.driver.find_elements(*locator)
        self.log.debug("Encontrados %d elementos con %s", len(elementos), describe(locator))
        return elementos

    def click(self, locator):
        self.log.debug("Click en: %s", describe(locator))
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text, sensitive=False):
        valor_logueado = "*****" if sensitive else text
        self.log.debug("Escribiendo '%s' en: %s", valor_logueado, describe(locator))
        elemento = self.find(locator)
        elemento.clear()
        elemento.send_keys(text)

    def get_text(self, locator):
        texto = self.find(locator).text
        self.log.debug("Texto leido de %s: '%s'", describe(locator), texto)
        return texto

    def is_visible(self, locator):
        return self.find(locator).is_displayed()

    def wait_for_url(self, fragment):
        self.log.debug("Esperando que la URL contenga: %s", fragment)
        self.wait.until(EC.url_contains(fragment))

