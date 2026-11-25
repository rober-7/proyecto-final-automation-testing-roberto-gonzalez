# Framework de Automatización de Pruebas — Tienda online + API

**Autor:** Roberto González · Proyecto final del curso de *Automation Testing* (QA)

---

## Resumen

Framework de automatización de pruebas que valida, sin intervención manual, el funcionamiento de una tienda online de práctica ([saucedemo.com](https://www.saucedemo.com/)) y de una API REST pública.

Las pruebas automatizadas ejecutan en un navegador real los mismos recorridos que haría un cliente (inicio de sesión, navegación del catálogo, carrito y compra completa) y verifican en cada paso que el sistema responda de la forma esperada. Ante una falla, el framework genera automáticamente:

- **una captura de pantalla** del momento exacto del error,
- **un registro detallado** (log) de cada paso ejecutado,
- **un reporte HTML** con el resultado y la duración de cada prueba.

También incluye pruebas de **API**, la interfaz que usan las aplicaciones para intercambiar datos entre sí (por ejemplo, una app móvil con su servidor). Se valida que las consultas, altas y bajas de información devuelvan las respuestas correctas, tanto en escenarios exitosos como de error.

### Demostración

![Ejecución automatizada de una compra completa y de dos escenarios de error](docs/img/demo_automatizacion.gif)

*Ejecución real de las pruebas. El recuadro rojo indica el elemento sobre el que se actúa y el cartel inferior describe la verificación que se realiza. En verde, el resultado esperado; en rojo, los escenarios de error que se provocan de forma deliberada.*

### Valor para el negocio

| Pruebas manuales | Pruebas automatizadas con este framework |
|---|---|
| Repetición manual de las mismas pruebas antes de cada versión | Ejecución completa con un solo comando |
| Horas de trabajo por ciclo de pruebas | Un par de minutos |
| Riesgo de omitir casos | La misma cobertura en cada ejecución |
| Fallas difíciles de reproducir | Evidencia automática: captura, log y reporte |

### Competencias aplicadas

- **Diseño de casos de prueba**: escenarios positivos y negativos (credenciales inválidas, usuario bloqueado, campos obligatorios vacíos).
- **Arquitectura mantenible**: patrón *Page Object Model*. Un cambio en la interfaz se corrige en un único lugar.
- **Pruebas guiadas por datos** (*data-driven testing*): los casos se definen en archivos CSV y JSON. Incorporar uno nuevo no requiere modificar código.
- **Evidencia y trazabilidad**: reportes, capturas de pantalla y logs detallados.
- **Control de versiones con Git**: cada funcionalidad se desarrolló en una rama dedicada y se integró mediante *merge* (ver historial de commits).

### Flujo cubierto

Recorrido de compra validado de punta a punta. Las flechas punteadas representan los **escenarios negativos**: se ingresan datos inválidos de forma deliberada para verificar que el sistema muestre el mensaje de error correspondiente.

```mermaid
flowchart LR
    A["Inicio de sesión"] --> B["Catálogo"]
    B --> C["Agregar productos"]
    C --> D["Carrito"]
    D --> E["Datos del comprador"]
    E --> F["Resumen y total"]
    F --> G["Compra confirmada"]
    A -. "usuario bloqueado o clave incorrecta" .-> X["Mensaje de error"]
    E -. "formulario incompleto" .-> Y["Mensaje de error"]
```

### Evidencia paso a paso

<table>
  <tr>
    <td width="50%"><img src="docs/img/01_login.png" alt="Paso 1: ingreso de usuario y contraseña"></td>
    <td width="50%"><img src="docs/img/02_catalogo.png" alt="Paso 2: verificación del catálogo"></td>
  </tr>
  <tr>
    <td><img src="docs/img/03_agregar_productos.png" alt="Paso 3: se agregan dos productos y el carrito indica 2"></td>
    <td><img src="docs/img/04_carrito.png" alt="Paso 4: verificación del contenido del carrito"></td>
  </tr>
  <tr>
    <td><img src="docs/img/05_datos_comprador.png" alt="Paso 5: carga de los datos del comprador"></td>
    <td><img src="docs/img/06_resumen_total.png" alt="Paso 6: verificación de subtotal, impuesto y total"></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><img src="docs/img/07_compra_confirmada.png" alt="Compra confirmada" width="50%"></td>
  </tr>
</table>

**Escenarios negativos**: se fuerzan errores de forma deliberada para verificar que el sistema los detecte y los informe correctamente.

<table>
  <tr>
    <td width="50%"><img src="docs/img/08_error_usuario_bloqueado.png" alt="Usuario bloqueado: el sistema muestra el mensaje de error"></td>
    <td width="50%"><img src="docs/img/09_error_formulario_incompleto.png" alt="Formulario sin nombre: el sistema muestra el mensaje de error"></td>
  </tr>
</table>

### Cobertura actual

| Área | Qué se verifica | Casos |
|---|---|---|
| Inicio de sesión | Acceso de usuarios válidos y mensaje de error correcto para usuarios inválidos o bloqueados | 6 |
| Catálogo | Visualización de productos, precios, menú y filtro de orden | 4 |
| Carrito | Que cada producto agregado figure en el carrito con el precio correcto | 4 |
| Compra (checkout) | Compra completa de punta a punta, cálculo del total (productos + impuestos) y validación de campos obligatorios | 5 |
| API REST | Consultas, altas y bajas; respuesta ante recursos inexistentes; peticiones encadenadas | 9 |
| | **Total** | **28** |

> **En desarrollo:** ejecución continua en GitHub Actions.

### Reporte de resultados

Cada ejecución genera un reporte HTML con el estado y la duración de cada prueba. Cuando una prueba de interfaz falla, el reporte incluye el error exacto, el registro de pasos y **la captura de pantalla del momento de la falla**, sin necesidad de reproducir el problema.

![Reporte HTML con una prueba fallida y su captura de pantalla incrustada](docs/img/reporte_html.png)

*Ejemplo con una falla provocada deliberadamente para ilustrar el reporte: se esperaba un precio de $19.99 y el sitio muestra $29.99. A la derecha, la captura tomada automáticamente en ese instante.*

### Caso de estudio: diagnóstico de pruebas inestables

Al incorporar el flujo de compra, algunas pruebas comenzaron a fallar de forma intermitente. A partir de las capturas y los logs que genera el propio framework se identificó la causa: después del inicio de sesión, Chrome mostraba una alerta de *"contraseña filtrada"* (la tienda de práctica utiliza una clave pública) que bloqueaba las interacciones con la página.

La solución consistió en desactivar esa alerta en la configuración del navegador de pruebas y en agregar una espera explícita hasta que el carrito refleje cada producto agregado. Con estos cambios, la suite se ejecuta completa de forma estable.

> Las pruebas inestables (*flaky tests*) son uno de los problemas más frecuentes en automatización. Este caso muestra el valor de contar con buena evidencia (capturas y logs) para reducir el tiempo de diagnóstico.

---

## Parte técnica

### Tecnologías utilizadas

| Herramienta | Para qué se usa |
|---|---|
| **Python 3.12** | Lenguaje principal |
| **Pytest** | Framework de testing (fixtures, parametrización, hooks) |
| **Selenium WebDriver 4** | Automatización del navegador Chrome |
| **Requests** | Pruebas de API REST |
| **pytest-html** | Reporte HTML de la ejecución |
| **webdriver-manager** | Descarga automática del ChromeDriver compatible |
| **logging** (módulo estándar) | Registro de pasos de la ejecución |
| **Git + GitHub** | Control de versiones (una rama por funcionalidad) |

### Estructura del proyecto

```
proyecto-final-automation-testing-roberto-gonzalez/
├── pages/                     # Page Objects: CÓMO se interactúa con cada página
│   ├── base_page.py           #   Clase base: esperas explícitas y acciones comunes
│   ├── login_page.py          #   Pantalla de login
│   ├── inventory_page.py      #   Catálogo de productos
│   ├── cart_page.py           #   Carrito
│   ├── checkout_info_page.py      # Checkout paso 1: datos del comprador
│   ├── checkout_overview_page.py  # Checkout paso 2: resumen y total
│   └── checkout_complete_page.py  # Checkout final: confirmación
├── tests/                     # Casos de prueba: QUÉ se verifica
│   ├── conftest.py            #   Driver de Chrome, capturas ante fallos, log de resultados
│   ├── ui/                    #   Pruebas de interfaz (Selenium)
│   │   ├── conftest.py        #     Fixture de sesión iniciada
│   │   ├── test_login.py      #     Login parametrizado desde CSV
│   │   ├── test_catalogo.py   #     Catálogo
│   │   ├── test_carrito.py    #     Carrito parametrizado desde JSON
│   │   └── test_checkout.py   #     Compra de punta a punta + formulario incompleto
│   └── api/                   #   Pruebas de API (Requests)
│       ├── conftest.py        #     Fixtures del cliente de API
│       ├── test_posts.py      #     GET, POST, DELETE y caso 404 sobre /posts
│       └── test_flujos_encadenados.py  # Peticiones que dependen de la anterior
├── data/                      # Datos de prueba externos
│   ├── usuarios_login.csv     #   Usuarios y resultado esperado del login
│   ├── productos.json         #   Productos a agregar y su precio esperado
│   ├── checkout.json          #   Comprador, productos a comprar y formularios incompletos
│   ├── esperados.json         #   Usuario válido y textos esperados
│   └── api.json               #   URL de la API, ids a consultar y post a crear
├── utils/                     # Herramientas de soporte
│   ├── logger.py              #   Logger del framework
│   ├── data_reader.py         #   Lectura de CSV y JSON
│   ├── driver_factory.py      #   Creación de Chrome con la configuración común
│   └── api_client.py          #   Cliente HTTP (Requests) con logging y validación de estructura
├── scripts/
│   └── generar_evidencia_visual.py  # Genera las capturas y el GIF del README
├── docs/img/                  # Imágenes del README (capturas paso a paso y GIF)
├── reports/                   # Salidas de la ejecución
│   ├── reporte.html           #   Reporte HTML de la última ejecución (con capturas incrustadas)
│   ├── screenshots/           #   Capturas automáticas de tests fallidos
│   └── logs/execution.log     #   Log detallado de la última ejecución
├── pytest.ini                 # Configuración de pytest y del logging
└── requirements.txt
```

```mermaid
flowchart LR
    subgraph DATA["data/ · datos de prueba"]
        D1["CSV y JSON"]
    end
    subgraph TESTS["tests/ · QUÉ se verifica"]
        T1["ui/ · login · catálogo<br/>carrito · checkout"]
        T2["api/ · posts<br/>flujos encadenados"]
    end
    subgraph PAGES["pages/ · CÓMO se interactúa"]
        P1["LoginPage · InventoryPage · CartPage<br/>CheckoutInfo · Overview · Complete"]
    end
    D1 -- "utils/data_reader" --> T1
    T1 -- "acciones de negocio" --> P1
    P1 -- "Selenium WebDriver" --> WEB[("saucedemo.com")]
    D1 --> T2
    T2 -- "utils/api_client (Requests)" --> API[("jsonplaceholder<br/>.typicode.com")]
    T1 -. "conftest + utils/logger" .-> R["reports/<br/>HTML · capturas · log"]
    T2 -.-> R
```

**Separación de responsabilidades:** los tests nunca usan Selenium directamente. Le piden acciones a las páginas (`login_page.login(usuario, clave)`), y las páginas son las únicas que conocen los localizadores. Si cambia un elemento del sitio, se corrige en un solo archivo de `pages/`.

### Instalación de dependencias

Requisitos: **Python 3.10+** y **Google Chrome** instalado.

```bash
git clone https://github.com/rober-7/proyecto-final-automation-testing-roberto-gonzalez.git
cd proyecto-final-automation-testing-roberto-gonzalez

python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / Mac

pip install -r requirements.txt
```

No es necesario descargar ChromeDriver: `webdriver-manager` lo descarga automáticamente según la versión de Chrome instalada.

### Cómo ejecutar las pruebas

El reporte HTML se genera en cada ejecución (configurado en `pytest.ini`), por lo que no es necesario indicarlo en el comando.

```bash
# Toda la suite (UI + API)
pytest

# Sin abrir la ventana del navegador (más rápido, ideal para CI)
pytest --headless

# Ver los pasos del log en vivo en la consola
pytest --headless --log-cli-level=INFO

# Solo UI o solo API (marcadores asignados automáticamente según la carpeta)
pytest -m ui --headless
pytest -m api

# Solo un archivo o un caso
pytest tests/ui/test_login.py
pytest tests/ui/test_carrito.py
pytest tests/ui/test_checkout.py
pytest -k "bloqueado"            # por nombre de caso
```

### Datos de prueba y parametrización

Los datos están separados del código, en `data/`. Cada fila o elemento se convierte en un caso de prueba independiente gracias a `@pytest.mark.parametrize`.

**`data/usuarios_login.csv`**: cada fila es un caso de login.

| caso | username | password | resultado_esperado | mensaje_error |
|---|---|---|---|---|
| usuario_estandar | standard_user | secret_sauce | exito | |
| usuario_bloqueado | locked_out_user | secret_sauce | error | Epic sadface: Sorry, this user has been locked out. |
| … | | | | |

La columna `caso` es el nombre con el que aparece el test en el reporte, por ejemplo `test_login_fallido_muestra_mensaje_de_error[usuario_bloqueado]`. **Para incorporar un caso nuevo basta con agregar una fila al CSV.**

**`data/productos.json`**: lista de productos con su precio esperado. El test agrega cada uno al carrito y verifica que aparezca con ese precio.

**`data/checkout.json`**: datos del comprador, productos a comprar, tasa de impuesto esperada (8 %) y los formularios incompletos con el mensaje de error que debe mostrar cada uno.

**`data/api.json`**: URL base de la API, ids de posts a consultar (el test se repite por cada uno), id inexistente para el caso de error y el post a crear.

### Pruebas de API

Se prueban sobre [JSONPlaceholder](https://jsonplaceholder.typicode.com), una API REST pública de práctica. El cliente `utils/api_client.py` centraliza la URL base, el timeout y el registro en el log de cada petición y respuesta.

| Test | Método | Qué valida |
|---|---|---|
| `test_listar_posts_devuelve_todos_con_estructura_valida` | GET | 200, `Content-Type` JSON, 100 posts con campos y tipos correctos |
| `test_obtener_post_por_id[1, 50, 100]` | GET | 200, estructura y que el `id` devuelto sea el pedido |
| `test_obtener_post_inexistente_devuelve_404` | GET | **Escenario de error**: 404 y cuerpo vacío |
| `test_crear_post_devuelve_201_con_los_datos_enviados` | POST | 201, id asignado y que devuelva los mismos datos enviados |
| `test_eliminar_post_devuelve_200_y_cuerpo_vacio` | DELETE | 200 y cuerpo vacío |
| `test_obtener_usuario_y_luego_sus_posts` | GET → GET | **Encadenado**: el `id` del usuario se usa para pedir sus posts |
| `test_obtener_primer_post_del_usuario_y_luego_sus_comentarios` | GET → GET | **Encadenado**: el `id` del post se usa para pedir sus comentarios |

La estructura de cada respuesta se valida con `assert_estructura(objeto, esquema)`, que verifica que estén exactamente los campos esperados y con el tipo correcto. Por ejemplo, `{"id": int, "title": str}`.

En el log, cada petición queda registrada con su método, URL, código de respuesta, tiempo y cuerpo:

```
[INFO ] framework.api.client: --> POST https://jsonplaceholder.typicode.com/posts
[DEBUG] framework.api.client: Cuerpo enviado: {"title": "Automatizacion de pruebas con Python", ...}
[INFO ] framework.api.client: <-- 201 Created (931 ms)
```

> JSONPlaceholder simula las escrituras: el POST y el DELETE responden como si funcionaran, pero no guardan cambios. Por eso los flujos encadenados usan recursos relacionados (usuario → posts → comentarios) en lugar de "crear y luego consultar".

### Cómo interpretar los resultados

#### Reporte HTML: `reports/reporte.html`

Es un archivo autocontenido (incluye estilos e imágenes) que se abre con cualquier navegador. Contiene:

| Sección | Qué muestra |
|---|---|
| **Environment** | Versión de Python y librerías, sitio y API bajo prueba, navegador utilizado |
| **Summary** | Cantidad de pruebas *Passed*, *Failed*, *Errors* y *Skipped*, y la duración total. Las casillas permiten filtrar la tabla por estado |
| **Tabla de resultados** | Una fila por prueba con su estado, tipo (**UI** o **API**), nombre y duración. Las pruebas parametrizadas muestran el caso entre corchetes, por ejemplo `[usuario_bloqueado]` |
| **Detalle de cada prueba** | Al expandir una fila se ve el registro de pasos (*Captured log*). Si la prueba falló, también el error exacto con los valores esperado y obtenido, y **la captura de pantalla incrustada** |

Las pruebas fallidas aparecen expandidas por defecto, para ir directo al problema.

#### Capturas de pantalla: `reports/screenshots/`

Cuando una prueba de UI falla, además de incrustarse en el reporte, la captura se guarda como archivo con el nombre del test y la fecha/hora, por ejemplo `test_login_fallido_muestra_mensaje_de_error_usuario_bloqueado_20261125_015734.png`. Estos archivos no se versionan en git porque se generan en cada ejecución.

#### Log de ejecución: `reports/logs/execution.log`

Registro detallado de la última ejecución. Cada test aparece delimitado por `INICIO` y `RESULTADO`:

```
2026-11-18 22:16:32 [INFO   ] framework.conftest: ========== INICIO: tests/ui/test_login.py::... ==========
2026-11-18 22:16:32 [INFO   ] framework.conftest: Iniciando Chrome (headless=True)
2026-11-18 22:16:35 [INFO   ] framework.pages.LoginPage: Iniciando sesion con usuario 'standard_user'
2026-11-18 22:16:35 [DEBUG  ] framework.pages.LoginPage: Escribiendo '*****' en: id=password
2026-11-18 22:16:36 [INFO   ] framework.conftest: RESULTADO: tests/ui/test_login.py::... -> PASSED (1.06s)
```

| Nivel | Significado |
|---|---|
| `INFO` | Paso de negocio (login, agregar al carrito, resultado del test) |
| `DEBUG` | Acción técnica sobre un elemento (click, escribir, esperar) |
| `WARNING` | Se guardó una captura de pantalla |
| `ERROR` | Un test falló; incluye el detalle del error |

Las contraseñas se enmascaran (`*****`) en el log.

### Imágenes del README

Las capturas y el GIF de este README **no se editan manualmente**: los genera un script que recorre la tienda con los mismos Page Objects que usan los tests. En cada paso inyecta en la página el recuadro rojo y el cartel explicativo antes de tomar la captura. Para regenerarlas (por ejemplo, ante cambios en el sitio):

```bash
python scripts/generar_evidencia_visual.py
```

Las imágenes se guardan en `docs/img/`. El GIF se arma con Pillow, incluida en `requirements.txt`.

### Independencia de los tests

Cada test abre su propio navegador y, si lo necesita, inicia su propia sesión con el fixture `inventory_page`. Por eso la falla de un test no afecta a los demás, y los tests pueden ejecutarse en cualquier orden o de forma individual.
