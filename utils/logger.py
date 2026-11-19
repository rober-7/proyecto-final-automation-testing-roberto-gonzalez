"""Logger del framework.

Todos los modulos (pages, tests, conftest) piden su logger con `get_logger(__name__)`.
Los loggers cuelgan de "framework", y pytest se encarga de los destinos
segun lo configurado en pytest.ini:

- Archivo:  reports/logs/execution.log  (se sobrescribe en cada ejecucion)
- Reporte:  seccion "Captured log" de cada test en el reporte HTML
- Consola:  con `pytest --log-cli-level=INFO` se ven los pasos en vivo
"""

import logging

FRAMEWORK_LOGGER_NAME = "framework"


def get_logger(name):
    """Devuelve un logger hijo de "framework" (ej: framework.pages.login_page)."""
    logger = logging.getLogger(f"{FRAMEWORK_LOGGER_NAME}.{name}")
    logger.setLevel(logging.DEBUG)
    return logger
