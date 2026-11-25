"""Fixtures y hooks compartidos por todos los tests.

- `driver`: crea y cierra el navegador Chrome para cada test (tests independientes).
- `pytest_runtest_makereport`: registra el resultado de cada test en el log y,
  si un test de UI falla, guarda una captura de pantalla en reports/screenshots/
  y la incrusta en el reporte HTML.
- Hooks de pytest-html: titulo del reporte, datos del entorno y columna "Tipo".

Uso (el reporte reports/reporte.html se genera siempre, ver pytest.ini):
    pytest tests/                        # con ventana de Chrome visible
    pytest tests/ --headless             # sin interfaz grafica (mas rapido, ideal para CI)
    pytest tests/ --log-cli-level=INFO   # muestra los pasos del log en la consola
    pytest -m api                        # solo pruebas de API
    pytest -m ui --headless              # solo pruebas de UI
"""

import base64
import logging
import os
import re
from datetime import datetime

import pytest
from pytest_metadata.plugin import metadata_key

from pages.base_page import BASE_URL

from utils.driver_factory import create_chrome_driver
from utils.data_reader import read_json
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

    # Datos del entorno que se muestran en la seccion "Environment" del reporte HTML
    entorno = config.stash[metadata_key]
    entorno["Sitio bajo prueba (UI)"] = BASE_URL
    entorno["API bajo prueba"] = read_json("api.json")["base_url"]
    entorno["Navegador"] = "Chrome (headless)" if config.getoption("--headless") else "Chrome"


def pytest_html_report_title(report):
    report.title = "Reporte de pruebas · Proyecto final Automation Testing"


def pytest_html_results_table_header(cells):
    cells.insert(1, "<th>Tipo</th>")


def pytest_html_results_table_row(report, cells):
    cells.insert(1, f"<td>{getattr(report, 'tipo', '')}</td>")


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
    report.tipo = "API" if "api" in item.keywords else "UI"

    if report.when == "call" or (report.when == "setup" and not report.passed):
        resultado = report.outcome.upper()
        log.info("RESULTADO: %s -> %s (%.2fs)", item.nodeid, resultado, report.duration)
        if report.failed:
            log.error("Detalle del fallo en %s:\n%s", item.name, report.longreprtext)

    if report.when in ("setup", "call") and report.failed:
        navegador = item.funcargs.get("driver")
        if navegador is not None:
            guardar_captura_de_fallo(item, report, navegador)


def guardar_captura_de_fallo(item, report, navegador):
    """Guarda la captura en reports/screenshots/ y la incrusta en el reporte HTML."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_test = re.sub(r"[^\w\-]+", "_", item.name).strip("_")
    ruta = os.path.join(SCREENSHOTS_DIR, f"{nombre_test}_{timestamp}.png")
    navegador.save_screenshot(ruta)
    log.warning("Captura de pantalla guardada: %s", ruta)

    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is not None:
        with open(ruta, "rb") as archivo:
            imagen_base64 = base64.b64encode(archivo.read()).decode("ascii")
        extras = getattr(report, "extras", [])
        extras.append(pytest_html.extras.png(imagen_base64, name=os.path.basename(ruta)))
        report.extras = extras
