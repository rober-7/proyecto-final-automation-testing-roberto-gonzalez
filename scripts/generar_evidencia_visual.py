"""Genera las imagenes del README: capturas paso a paso y un GIF de la ejecucion.

Recorre saucedemo.com con los mismos Page Objects que usan los tests. En cada
paso resalta en rojo el elemento con el que interactua y muestra un cartel
explicativo, luego guarda la captura en docs/img/. Al final arma el GIF.

Uso (desde la raiz del proyecto):
    python scripts/generar_evidencia_visual.py
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from PIL import Image  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402

from pages import (  # noqa: E402
    CartPage,
    CheckoutCompletePage,
    CheckoutInfoPage,
    CheckoutOverviewPage,
    InventoryPage,
    LoginPage,
)
from utils.data_reader import read_csv, read_json  # noqa: E402
from utils.driver_factory import create_chrome_driver  # noqa: E402

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "docs", "img")
WINDOW_SIZE = (1280, 860)
GIF_WIDTH = 960
GIF_FRAME_MS = 2200

CHECKOUT = read_json("checkout.json")
ESPERADOS = read_json("esperados.json")
USUARIO_BLOQUEADO = next(u for u in read_csv("usuarios_login.csv") if u["caso"] == "usuario_bloqueado")

# Estilos que se inyectan en la pagina para el cartel y el resaltado
CSS_EVIDENCIA = """
#qa-cartel {
  position: fixed; left: 0; right: 0; bottom: 0; z-index: 99999; pointer-events: none;
  padding: 16px 28px; font: 600 24px/1.3 'Segoe UI', Arial, sans-serif;
  color: #fff; background: rgba(19, 35, 47, .93); box-shadow: 0 -4px 16px rgba(0,0,0,.25);
}
#qa-cartel small { display: block; font-weight: 400; font-size: 17px; opacity: .8; }
#qa-cartel.ok { background: rgba(27, 110, 52, .95); }
#qa-cartel.error { background: rgba(150, 30, 30, .95); }
.qa-resaltado { outline: 4px solid #e53935 !important; outline-offset: 3px; border-radius: 4px; }
.qa-marcador { background: #fff176 !important; box-shadow: 0 0 0 3px #fff176; border-radius: 2px; }
"""


def mostrar_cartel(driver, titulo, detalle="", tipo=""):
    driver.execute_script(
        """
        if (!document.getElementById('qa-estilos')) {
            const estilo = document.createElement('style');
            estilo.id = 'qa-estilos';
            estilo.textContent = arguments[0];
            document.head.appendChild(estilo);
        }
        let cartel = document.getElementById('qa-cartel');
        if (!cartel) {
            cartel = document.createElement('div');
            cartel.id = 'qa-cartel';
            document.body.appendChild(cartel);
        }
        cartel.className = arguments[3];
        cartel.innerHTML = arguments[1] + (arguments[2] ? '<small>' + arguments[2] + '</small>' : '');
        """,
        CSS_EVIDENCIA, titulo, detalle, tipo,
    )


def resaltar(driver, locators, clase="qa-resaltado"):
    """Marca los elementos: recuadro rojo (qa-resaltado) o fondo amarillo (qa-marcador)."""
    for locator in locators:
        elemento = driver.find_element(*locator)
        driver.execute_script(
            "arguments[0].classList.add(arguments[1]);"
            # Solo desplaza la pagina si el elemento queda fuera de vista o tapado por el cartel
            "const r = arguments[0].getBoundingClientRect();"
            "if (r.top < 60 || r.bottom > window.innerHeight - 110)"
            "  arguments[0].scrollIntoView({block: 'center'});",
            elemento, clase,
        )


def limpiar(driver):
    """Quita el cartel y el resaltado para que no interfieran con el siguiente paso."""
    driver.execute_script(
        "document.getElementById('qa-cartel')?.remove();"
        "document.querySelectorAll('.qa-resaltado, .qa-marcador')"
        ".forEach(e => e.classList.remove('qa-resaltado', 'qa-marcador'));"
    )


def esperar_imagenes(driver):
    """Espera a que terminen de cargar las imagenes visibles (iconos, fotos de productos)."""
    WebDriverWait(driver, 10).until(lambda d: d.execute_script(
        "return Array.from(document.images).every(img => img.complete && img.naturalWidth > 0);"
    ))


def capturar(driver, nombre_archivo, titulo, detalle="", tipo="", resaltados=(), marcados=()):
    esperar_imagenes(driver)
    resaltar(driver, resaltados)
    resaltar(driver, marcados, clase="qa-marcador")
    mostrar_cartel(driver, titulo, detalle, tipo)
    ruta = os.path.join(OUTPUT_DIR, nombre_archivo)
    driver.save_screenshot(ruta)
    limpiar(driver)
    print(f"  captura: docs/img/{nombre_archivo}")
    return ruta


def recorrer_compra_exitosa(driver):
    """Flujo feliz: login -> catalogo -> carrito -> datos -> resumen -> confirmacion."""
    capturas = []
    usuario = ESPERADOS["usuario_valido"]
    comprador = CHECKOUT["comprador"]

    login_page = LoginPage(driver).load()
    login_page.type(LoginPage.USERNAME_INPUT, usuario["username"])
    login_page.type(LoginPage.PASSWORD_INPUT, usuario["password"])
    capturas.append(capturar(
        driver, "01_login.png", "Paso 1 · Inicio de sesión",
        f"Se ingresan el usuario '{usuario['username']}' y la contraseña",
        resaltados=[LoginPage.USERNAME_INPUT, LoginPage.PASSWORD_INPUT],
    ))
    login_page.click(LoginPage.LOGIN_BUTTON)

    inventory_page = InventoryPage(driver).wait_until_loaded()
    capturas.append(capturar(
        driver, "02_catalogo.png", "Paso 2 · Catálogo de productos",
        "Se verifica el título 'Products', los productos y sus precios",
        resaltados=[InventoryPage.PAGE_TITLE],
    ))

    for nombre in CHECKOUT["productos"]:
        inventory_page.add_product_to_cart(nombre)
    driver.execute_script("window.scrollTo(0, 0);")
    capturas.append(capturar(
        driver, "03_agregar_productos.png", "Paso 3 · Productos agregados al carrito",
        f"{' y '.join(CHECKOUT['productos'])} · el contador del carrito indica {len(CHECKOUT['productos'])}",
        resaltados=[InventoryPage.CART_BADGE],
    ))

    inventory_page.go_to_cart()
    cart_page = CartPage(driver).wait_until_loaded()
    capturas.append(capturar(
        driver, "04_carrito.png", "Paso 4 · Verificación del carrito",
        "Se verifica que figuren los productos elegidos con su precio",
        resaltados=[CartPage.CART_LIST],
    ))

    cart_page.go_to_checkout()
    info_page = CheckoutInfoPage(driver).wait_until_loaded()
    info_page.fill_buyer_info(comprador["nombre"], comprador["apellido"], comprador["codigo_postal"])
    capturas.append(capturar(
        driver, "05_datos_comprador.png", "Paso 5 · Datos del comprador",
        "Nombre, apellido y código postal tomados de data/checkout.json",
        resaltados=[CheckoutInfoPage.FIRST_NAME_INPUT, CheckoutInfoPage.LAST_NAME_INPUT,
                    CheckoutInfoPage.POSTAL_CODE_INPUT],
    ))

    info_page.click_continue()
    overview_page = CheckoutOverviewPage(driver).wait_until_loaded()
    subtotal, impuesto, total = overview_page.get_subtotal(), overview_page.get_tax(), overview_page.get_total()
    capturas.append(capturar(
        driver, "06_resumen_total.png", "Paso 6 · Verificación del total",
        f"${subtotal} (productos) + ${impuesto} (impuesto 8 %) = ${total}",
        marcados=[CheckoutOverviewPage.SUBTOTAL_LABEL, CheckoutOverviewPage.TAX_LABEL,
                  CheckoutOverviewPage.TOTAL_LABEL],
    ))

    overview_page.finish_purchase()
    complete_page = CheckoutCompletePage(driver).wait_until_loaded()
    capturas.append(capturar(
        driver, "07_compra_confirmada.png", "✔ Compra confirmada",
        f"Se verifica el mensaje de confirmación '{complete_page.get_confirmation_message()}'",
        tipo="ok", resaltados=[CheckoutCompletePage.COMPLETE_HEADER],
    ))
    return capturas


def recorrer_casos_negativos(driver):
    """Casos negativos: el sitio debe mostrar el mensaje de error correcto."""
    capturas = []

    login_page = LoginPage(driver).load()
    login_page.login(USUARIO_BLOQUEADO["username"], USUARIO_BLOQUEADO["password"])
    login_page.get_error_message()
    capturas.append(capturar(
        driver, "08_error_usuario_bloqueado.png", "✘ Escenario negativo · Usuario bloqueado",
        "El sistema rechaza el acceso y muestra el mensaje de error esperado",
        tipo="error", resaltados=[LoginPage.ERROR_MESSAGE],
    ))

    usuario = ESPERADOS["usuario_valido"]
    login_page = LoginPage(driver).load()
    login_page.login(usuario["username"], usuario["password"])
    inventory_page = InventoryPage(driver).wait_until_loaded()
    inventory_page.add_product_to_cart(CHECKOUT["productos"][0])
    inventory_page.go_to_cart()
    CartPage(driver).wait_until_loaded().go_to_checkout()
    info_page = CheckoutInfoPage(driver).wait_until_loaded()
    info_page.fill_buyer_info("", "Gonzalez", "1425")
    info_page.click_continue()
    info_page.get_error_message()
    capturas.append(capturar(
        driver, "09_error_formulario_incompleto.png", "✘ Escenario negativo · Formulario incompleto",
        "Sin nombre, el sistema impide continuar y muestra 'First Name is required'",
        tipo="error", resaltados=[CheckoutInfoPage.ERROR_MESSAGE, CheckoutInfoPage.FIRST_NAME_INPUT],
    ))
    return capturas


def armar_gif(rutas, nombre_archivo):
    cuadros = []
    for ruta in rutas:
        imagen = Image.open(ruta).convert("RGB")
        alto = round(imagen.height * GIF_WIDTH / imagen.width)
        imagen = imagen.resize((GIF_WIDTH, alto), Image.LANCZOS)
        cuadros.append(imagen.quantize(colors=128, method=Image.Quantize.MEDIANCUT))

    ruta_gif = os.path.join(OUTPUT_DIR, nombre_archivo)
    cuadros[0].save(
        ruta_gif, save_all=True, append_images=cuadros[1:],
        duration=GIF_FRAME_MS, loop=0, optimize=True,
    )
    print(f"  gif: docs/img/{nombre_archivo} ({os.path.getsize(ruta_gif) // 1024} KB)")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    driver = create_chrome_driver(headless=True, window_size=WINDOW_SIZE)
    try:
        print("Recorriendo la compra exitosa...")
        capturas_compra = recorrer_compra_exitosa(driver)
        print("Recorriendo los casos negativos...")
        capturas_negativas = recorrer_casos_negativos(driver)
    finally:
        driver.quit()

    print("Armando el GIF...")
    armar_gif(capturas_compra + capturas_negativas, "demo_automatizacion.gif")


if __name__ == "__main__":
    main()
