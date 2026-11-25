"""Cliente HTTP para las pruebas de API, construido sobre la biblioteca Requests.

Centraliza la URL base, el timeout y el registro en el log de cada peticion y
respuesta, para que los tests solo indiquen el metodo, el endpoint y los datos.
"""

import json

import requests

from utils.logger import get_logger

DEFAULT_TIMEOUT = 15
MAX_BODY_LOG_LENGTH = 500


class ApiClient:
    def __init__(self, base_url, timeout=DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json; charset=UTF-8"})
        self.log = get_logger("api.client")

    def request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        self.log.info("--> %s %s", method, url)
        if "json" in kwargs:
            self.log.debug("Cuerpo enviado: %s", json.dumps(kwargs["json"], ensure_ascii=False))

        respuesta = self.session.request(method, url, timeout=self.timeout, **kwargs)

        self.log.info(
            "<-- %s %s (%.0f ms)",
            respuesta.status_code, respuesta.reason, respuesta.elapsed.total_seconds() * 1000,
        )
        self.log.debug("Cuerpo recibido: %s", self._compact_body(respuesta)[:MAX_BODY_LOG_LENGTH])
        return respuesta

    @staticmethod
    def _compact_body(respuesta):
        """Devuelve el cuerpo en una sola linea (la API lo envia formateado en varias)."""
        try:
            return json.dumps(respuesta.json(), ensure_ascii=False)
        except ValueError:
            return respuesta.text

    def get(self, endpoint, **kwargs):
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.request("POST", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.request("DELETE", endpoint, **kwargs)

    def close(self):
        self.session.close()


def assert_estructura(objeto, esquema):
    """Verifica que el JSON tenga exactamente los campos del esquema y con el tipo esperado.

    Ejemplo: assert_estructura(post, {"id": int, "title": str})
    """
    assert set(objeto.keys()) == set(esquema.keys()), (
        f"Campos recibidos {sorted(objeto.keys())} != esperados {sorted(esquema.keys())}"
    )
    for campo, tipo in esquema.items():
        assert isinstance(objeto[campo], tipo), (
            f"El campo '{campo}' es {type(objeto[campo]).__name__}, se esperaba {tipo.__name__}"
        )
