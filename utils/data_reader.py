"""Lectura de datos de prueba desde archivos externos (carpeta data/).

Mantener los datos fuera del codigo permite agregar casos nuevos editando
un CSV o un JSON, sin tocar los tests.
"""

import csv
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def read_csv(filename):
    """Devuelve las filas del CSV como una lista de diccionarios (columna -> valor)."""
    with open(os.path.join(DATA_DIR, filename), newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def read_json(filename):
    with open(os.path.join(DATA_DIR, filename), encoding="utf-8") as archivo:
        return json.load(archivo)
