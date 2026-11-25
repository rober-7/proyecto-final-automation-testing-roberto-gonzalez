"""Creacion del navegador Chrome con la configuracion comun del framework.

La usan el fixture `driver` de los tests y el script que genera las
imagenes del README, para que ambos abran Chrome exactamente igual.
"""

import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def create_chrome_driver(headless=False, window_size=(1920, 1080)):
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
        options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")

    # En servidores de integracion continua (GitHub Actions define CI=true) Chrome
    # necesita estas opciones para funcionar dentro del contenedor
    if os.environ.get("CI"):
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)
