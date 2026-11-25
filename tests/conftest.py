"""Fixtures y hooks compartidos por todos los tests.

- `driver`: crea y cierra el navegador Chrome para cada test (tests independientes).
- `pytest_runtest_makereport`: registra el resultado de cada test en el log y,
  si un test de UI falla, guarda automaticamente una captura de pantalla en
  reports/screenshots/.

Uso:
    pytest tests/                        # con ventana de Chrome visible
    pytest tests/ --headless             # sin interfaz grafica (mas rapido, ideal para CI)
    pytest tests/ --log-cli-level=INFO   # muestra los pasos del log en la consola
    pytest -m api                        # solo pruebas de API
    pytest -m ui --headless              # solo pruebas de UI
"""

import logging
import os
from datetime import datetime

import pytest

from utils.driver_factory import create_chrome_driver
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


def pytest_collection_modifyitems(items):
    """Marca cada test como 'ui' o 'api' segun su carpeta (permite: pytest -m api)."""
    for item in items:
        carpeta = item.path.parent.name
        if carpeta in ("ui", "api"):
            item.add_marker(carpeta)


def pytest_runtest_logstart(nodeid, location):
    log.info("========== INICIO: %s ==========", nodeid)


@pytest.fixture
def driver(request):
    """Inicializa el WebDriver de Chrome para un test y lo cierra al finalizar."""
    headless = request.config.getoption("--headless")

    log.info("Iniciando Chrome (headless=%s)", headless)
    navegador = create_chrome_driver(headless=headless)

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
