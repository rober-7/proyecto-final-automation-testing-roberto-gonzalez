"""Fixtures y hooks compartidos por todos los tests.

- `driver`: crea y cierra el navegador Chrome para cada test (tests independientes).
- `pytest_runtest_makereport`: registra el resultado de cada test en el log y,
  si un test de UI falla, guarda automaticamente una captura de pantalla en
  reports/screenshots/.

Uso:
    pytest tests/                        # con ventana de Chrome visible
    pytest tests/ --headless             # sin interfaz grafica (mas rapido, ideal para CI)
    pytest tests/ --log-cli-level=INFO   # muestra los pasos del log en la consola
"""

import logging
import os
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from utils.logger import get_logger

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
SCREENSHOTS_DIR = os.path.join(REPORTS_DIR, "screenshots")
LOGS_DIR = os.path.join(REPORTS_DIR, "logs")

# Librerias externas muy verbosas en DEBUG: solo registramos sus advertencias
NOISY_LOGGERS = ("selenium", "urllib3", "WDM")

log = get_logger("conftest")


def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Ejecuta el navegador Chrome sin interfaz grafica (modo headless).",
    )


def pytest_configure(config):
    os.makedirs(LOGS_DIR, exist_ok=True)
    for nombre in NOISY_LOGGERS:
        logging.getLogger(nombre).setLevel(logging.WARNING)


def pytest_runtest_logstart(nodeid, location):
    log.info("========== INICIO: %s ==========", nodeid)


@pytest.fixture
def driver(request):
    """Inicializa el WebDriver de Chrome para un test y lo cierra al finalizar."""
    headless = request.config.getoption("--headless")
    options = Options()
    options.add_argument("--start-maximized")

    # Desactiva el gestor de contrasenas de Chrome. Sin esto, al hacer login con
    # 'secret_sauce' (una clave publica) Chrome muestra el aviso "contrasena filtrada",
    # que bloquea los clicks sobre la pagina y hace fallar los tests al azar.
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    options.add_argument("--disable-features=PasswordLeakDetection,PasswordCheck")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    log.info("Iniciando Chrome (headless=%s)", headless)
    service = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=service, options=options)

    yield navegador

    log.info("Cerrando Chrome")
    navegador.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Registra el resultado del test y genera una captura de pantalla si falla."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" or (report.when == "setup" and not report.passed):
        resultado = report.outcome.upper()
        log.info("RESULTADO: %s -> %s (%.2fs)", item.nodeid, resultado, report.duration)
        if report.failed:
            log.error("Detalle del fallo en %s:\n%s", item.name, report.longreprtext)

    if report.when == "call" and report.failed:
        navegador = item.funcargs.get("driver")
        if navegador is not None:
            os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"{item.name}_{timestamp}.png"
            ruta = os.path.join(SCREENSHOTS_DIR, nombre_archivo)
            navegador.save_screenshot(ruta)
            log.warning("Captura de pantalla guardada: %s", ruta)
