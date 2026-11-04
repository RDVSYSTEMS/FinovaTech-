# FinovaTech v10.3

Sistema de Finanzas Personales para Estudiantes de Bachillerato.
Aplicación web (HTML/CSS/JS + Flask + MySQL) con autenticación, control de
ingresos/gastos, presupuesto, notificaciones y agendamiento de sesiones. Proyecto de grado SENA —
desarrollado por **RDV Systems**.

> Nota de versionado: el historial que aparece abajo es una reconstrucción
> retrospectiva de las etapas del proyecto. El repositorio actual conserva la
> versión acumulada **v10.3.0**; las versiones anteriores representan hitos de
> desarrollo y no necesariamente commits publicados por separado.

## Requisitos previos

- Python 3.14 (última estable; probado con 3.14.8)
- XAMPP con Apache + MySQL/MariaDB (usuario `root`, sin contraseña)
- Git

## Instalación

```powershell
# 1. Entorno virtual
py -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 2. Configuración
copy .env.example .env     # completa SECRET_KEY (o genera una: python -c "import secrets; print(secrets.token_hex(32))")

# 3. Base de datos (con MySQL de XAMPP encendido; el puerto se define en .env)
$sql = Get-Content -Raw -LiteralPath "database\schema.sql"
$sql | C:\xampp\mysql\bin\mysql.exe -u root --default-character-set=utf8mb4

# 4. Datos de demostración
.venv\Scripts\python -m scripts.seed_demo
```

## Ejecutar

Doble clic en `iniciar.bat` (valida el puerto de MySQL de `.env` y abre el navegador) o:

```powershell
.venv\Scripts\python run.py
```

Servidor en http://localhost:5001

> El puerto se puede cambiar con la variable de entorno `PORT` (por defecto 5001).
>
> El puerto de MySQL se toma de `DB_PORT` en `.env` (por defecto 3306), y
> `iniciar.bat` comprueba ese mismo puerto. Si otro servicio ocupa el 3306,
> inicia MySQL de XAMPP en otro puerto y ajusta `DB_PORT`.

### Cuenta de demostración
- Correo: `adminr123@gmail.com`
- Contraseña: `123456789`

## Estructura del proyecto

```
FinovaTech v10/
├── run.py                  # Punto de entrada (create_app + run)
├── iniciar.bat             # Lanzador (verifica el puerto de MySQL de .env)
├── requirements.txt
├── .env / .env.example     # Configuración (NO subir .env a Git)
├── app/                    # Paquete de la aplicación
│   ├── __init__.py         # Fábrica create_app (factory pattern)
│   ├── config.py           # Config (variables de entorno)
│   ├── db.py               # Conexión MySQL (PyMySQL)
│   ├── seguridad.py        # CSRF, cabeceras, login_requerido, anti fuerza bruta
│   ├── blueprints/         # publicas, panel, registros, notificaciones
│   ├── modelos/            # usuarios.py, finanzas.py, agendamientos.py
│   ├── templates/          # Plantillas HTML
│   └── static/             # CSS, JS, imágenes, vendor
├── database/
│   └── schema.sql          # 8 tablas + triggers + procedures + vista
├── scripts/
│   └── seed_demo.py        # Datos de demostración repetibles
├── tests/
│   └── test_smoke.py       # Smoke tests (públicas, login, CSRF)
├── plans/                  # Planes de fase MIDEGS
│   ├── fase05_desarrollo_e_integracion.md
│   └── fase06_verificacion_validacion.md
└── docs/
    ├── REQUISITOS.md       # Documento SRS v10 (RF, RNF, criterios)
    ├── MODELO_DATOS.md     # ER v10, tablas, triggers, procedures, vista
    └── GUION_PRESENTACION.md  # Guion de demo para la presentación
```

## Seguridad

- Contraseñas cifradas (`werkzeug.security`).
- Token CSRF por sesión validado con `hmac.compare_digest`.
- Cookies HttpOnly + SameSite=Lax; rotación de sesión en login.
- Cabeceras HTTP (CSP, X-Frame-Options, nosniff, Referrer-Policy,
  Permissions-Policy).
- Bloqueo anti fuerza bruta (5 fallos → 2 min, duplicado progresivo).
- SQL con parámetros `%s` y nombres de tabla en lista blanca.

### Funcionamiento de la seguridad

#### 1. Contraseñas y autenticación

Las contraseñas se convierten en hashes mediante `generate_password_hash`
antes de guardarse en MySQL. Durante el login, `check_password_hash` compara
la contraseña recibida con el hash almacenado; la contraseña original nunca se
guarda ni se consulta directamente en SQL.

El registro público solo acepta los roles `estudiante` y `padre`.
El rol `administrador` no se puede crear desde el formulario público. Después
de un login correcto, la aplicación limpia la sesión anterior, genera un nuevo
token CSRF y guarda únicamente los datos necesarios para identificar al usuario:
`user_id`, `user_email`, `user_name` y `user_type`.

#### 2. Protección CSRF

La función global `csrf_proteger` se ejecuta antes de cada solicitud:

1. En una solicitud `GET` o `HEAD`, crea un token aleatorio de 64 caracteres
    hexadecimales si la sesión todavía no tiene uno.
2. El context processor expone ese token como `{{ csrf_token }}` para los
    formularios HTML.
3. En cada `POST`, compara el token de la sesión con el token enviado en el
    campo `csrf_token`.
4. Si falta o no coincide, la solicitud termina con HTTP 400 y no llega a la
    ruta que modifica datos.

La comparación usa `hmac.compare_digest`, que evita comparaciones simples
susceptibles a ataques de temporización. Por esta razón, todos los formularios
que crean, eliminan o modifican información deben incluir el token.

#### 3. Control de acceso

Las rutas privadas utilizan el decorador `login_requerido`. El decorador
comprueba que exista `user_email` en la sesión; si no existe, redirige a
`/login`. Las operaciones financieras también filtran por el `user_id` de la
sesión, de modo que un usuario no pueda consultar o eliminar movimientos de
otra cuenta.

#### 4. Protección contra fuerza bruta

El login registra los intentos fallidos usando la combinación de dirección IP
y correo. Después de cinco fallos se activa un bloqueo de dos minutos. Cada
nueva ronda de cinco fallos duplica el tiempo de bloqueo: 2, 4, 8 minutos,
etc. Un login correcto elimina el historial de fallos de esa combinación.

El sistema también elimina entradas antiguas cuando el diccionario en memoria
supera 5000 registros, evitando un crecimiento indefinido durante la ejecución
local.

#### 5. Protección contra inyección SQL

Los valores recibidos desde formularios se envían mediante parámetros `%s` de
PyMySQL. No se concatenan directamente dentro de las consultas. En las
operaciones donde cambia la tabla (`ingreso` o `gasto`), el nombre se obtiene
de una lista blanca fija, nunca del texto enviado por el usuario.

Las claves foráneas y los filtros por propietario también se aplican en la
base de datos. Por ejemplo, eliminar un movimiento exige simultáneamente su
identificador y el `estudiante_id` asociado a la sesión actual.

#### 6. Cookies y cabeceras HTTP

La sesión Flask usa `HttpOnly`, por lo que JavaScript no puede leer la cookie,
y `SameSite=Lax`, que reduce el envío de cookies en solicitudes externas.
Además, la aplicación agrega:

- `X-Frame-Options: DENY`: evita incrustar la aplicación en iframes.
- `X-Content-Type-Options: nosniff`: evita interpretar recursos con otro tipo.
- `Referrer-Policy`: limita la información enviada como referencia.
- `Permissions-Policy`: bloquea cámara, micrófono y geolocalización.
- `Content-Security-Policy`: restringe scripts, estilos, fuentes, imágenes,
  multimedia y conexiones a los orígenes autorizados.
- `Strict-Transport-Security`: se añade cuando la aplicación se ejecuta bajo
  HTTPS.

#### 7. Límites de la configuración actual

Esta configuración está pensada para el entorno educativo local con Flask y
XAMPP. Para producción se debería añadir HTTPS real, mantener una `SECRET_KEY`
aleatoria y privada, mover el límite de intentos a un almacenamiento compartido
como Redis y configurar una política de despliegue que no permita contraseñas
por defecto de MySQL.

## Pruebas

```powershell
.venv\Scripts\python -m tests.test_smoke
```

La suite smoke valida rápidamente la integración local:

- Rutas públicas y aliases `.html` de login y registro.
- Redirección de rutas protegidas cuando no existe sesión.
- Registro de un usuario con datos únicos.
- Login de la cuenta demo y acceso al panel.
- Acceso autenticado a la lista de movimientos.
- Rechazo de operaciones POST sin token CSRF.

Requiere MySQL/MariaDB encendido, el esquema aplicado y la cuenta demo
disponible. No reemplaza pruebas unitarias ni pruebas completas del navegador.

## Documentación técnica del código

Los archivos fuente incluyen comentarios y docstrings sobre sus decisiones
principales. La documentación está distribuida así:

- `app/db.py`: conexión a MySQL, configuración externa y `DictCursor`.
- `app/seguridad.py`: CSRF, sesiones, bloqueo progresivo y cabeceras HTTP.
- `app/__init__.py`: fábrica Flask y registro de blueprints.
- `app/blueprints/`: responsabilidad de cada grupo de rutas y validaciones.
- `app/modelos/`: usuarios, movimientos financieros, notificaciones y citas.
- `app/static/js/global.js`: navegación, formularios, agendamiento y eventos de interfaz.
- `app/static/vendor/aos.css`: estilos de las animaciones de aparición al hacer scroll.
- `app/static/vendor/aos.js`: biblioteca AOS inicializada desde `global.js`.
- `app/static/vendor/chart.umd.min.js`: biblioteca Chart.js usada para las gráficas del panel.
- `database/schema.sql`: tablas, relaciones, triggers, procedimientos y vista.
- `scripts/seed_demo.py`: datos demo, idempotencia y transacción de carga.
- `tests/test_smoke.py`: cobertura de rutas, autenticación y protección CSRF.
- `docs/REQUISITOS.md`: requisitos, rutas y contrato del agendamiento.
- `docs/MODELO_DATOS.md`: relaciones, persistencia y reglas de la base de datos.
- `docs/GUION_PRESENTACION.md`: recorrido de demo y checklist previo.
- `plans/`: planes de fase MIDEGS (perfil Estándar).

El cierre de sesión se realiza mediante `POST /logout` con `csrf_token`; no se
usa un enlace GET para cambiar el estado de la sesión.

Los comentarios explican responsabilidades, reglas de negocio y decisiones no
obvias; no repiten instrucciones línea por línea.

## Páginas web y sus funciones

### Páginas públicas

| Plantilla | Ruta | Funciones principales |
|---|---|---|
| `index.html` | `/` | Presenta FinovaTech, sus beneficios, estadísticas reales (usuarios y movimientos desde la base de datos) y una llamada a la acción final. |
| `login.html` | `/login` o `/login.html` | Recibe correo y contraseña, valida CSRF e inicia la sesión. Video de fondo, entrada escalonada y botón pulsante. |
| `registro.html` | `/registro` o `/registro.html` | Crea cuentas, valida rol, contraseña y confirmación. Validación en vivo por campo y video de fondo. |
| `contacto.html` | `/contacto.html` | Muestra información de contacto y créditos del proyecto. |
| `servicios.html` | `/servicios.html` | Catálogo de servicios con video de fondo; cada tarjeta dirige a `/login`. Incluye una llamada a la acción final. |
| `soporte.html` | `/soporte.html` | Valida localmente nombre, correo, asunto y mensaje de soporte. |
| `terminos.html` | `/terminos.html` | Explica las condiciones de uso de la plataforma. |

### Páginas protegidas

Estas páginas requieren una sesión iniciada. Sin sesión, Flask redirige a
`/login` mediante `login_requerido`.

| Plantilla | Ruta | Funciones principales |
|---|---|---|
| `panel.html` | `/panel` | Muestra ingresos, gastos, balance, registros, gráficas, presupuesto y movimientos recientes. |
| `lista.html` | `/lista` | Lista movimientos, permite buscar y filtrar, crear registros y eliminar los propios. |
| `notificacion.html` | `/notificacion` | Presenta alertas de presupuesto, gastos elevados y comportamiento mensual. |
| `agendamiento.html` | `/agendamiento` | Permite seleccionar fecha, hora, categoría, estado y comentarios de una sesión. |

### Funciones compartidas

- `app/static/js/global.js` crea el encabezado y pie de página dinámicos.
- El menú cambia según la ruta y ofrece navegación pública o autenticada.
- Los formularios protegidos incluyen `csrf_token`.
- El JavaScript controla menú móvil, contraseña visible, buscador, mensajes,
    animaciones, gráficas auxiliares y envío del agendamiento.
- El JavaScript también controla la barra de progreso de lectura y el parallax
    del hero (desactivado si el usuario prefiere movimiento reducido).
- `app/static/css/` contiene los estilos generales y los estilos específicos
    de cada página.

### Animaciones de la interfaz

Las páginas públicas (inicio y servicios) comparten un conjunto de animaciones
definidas en CSS, sin librerías adicionales (además de AOS). El panel reutiliza
el mismo lenguaje visual sin AOS, con entradas propias:

- **Entrada escalonada**: el encabezado y los botones aparecen con
    deslizamiento y desvanecido al cargar, con retardos progresivos. En el panel
    el sidebar entra desde la izquierda y las tarjetas de estadísticas suben una
    tras otra.
- **Aparición al hacer scroll**: gestionada por AOS mediante atributos `data-aos`.
- **Hover en imágenes**: zoom y brillo suave al pasar el mouse.
- **Cards con glow**: las tarjetas se elevan y muestran un brillo que las barre.
- **Botón pulsante**: el botón principal del bloque final emite un pulso suave.
- **Barra de progreso de lectura**: línea superior que crece según el desplazamiento
    (presente en inicio, servicios, login, registro y panel).
- **Parallax del hero**: la imagen del inicio se desplaza lentamente con el scroll.
- **Flotación**: las tarjetas de llamada a la acción "respiran" con un vaivén suave.

Todas respetan `prefers-reduced-motion`: si el usuario configura menos movimiento
en su sistema, las animaciones se desactivan.

### Validación de formularios

Los formularios de login y registro validan **en dos capas**:

1. **Cliente (JavaScript)**: al salir de cada campo (`blur`) y al enviar, se
    revisa el valor y se muestra un mensaje debajo del campo, marcándolo en
    rojo (error) o verde (correcto). Si algún campo es inválido, el envío se
    bloquea y el formulario vibra (`shake`) como aviso visual.
2. **Servidor (Flask + MySQL)**: es la fuente de verdad. Revalida campos
    obligatorios, formato, longitud de contraseña, coincidencia, rol permitido
    y duplicados; devuelve un mensaje que se muestra dentro de la tarjeta.

Mensajes del cliente (login): correo vacío o con formato inválido, contraseña
vacía o menor a 8 caracteres. Mensajes del cliente (registro): nombres,
correo, usuario (mínimo 4), contraseña (mínimo 8), confirmación coincidente y
tipo de usuario. Los errores del servidor (duplicados, rol no permitido,
contraseñas distintas) se muestran en la tarjeta del formulario.

### Dependencias frontend incluidas

Las bibliotecas de `app/static/vendor/` se sirven localmente para que la
interfaz no dependa de una conexión externa durante la ejecución:

- **AOS** (`aos.js` + `aos.css`) anima elementos con atributos `data-aos`.
- **Chart.js** (`chart.umd.min.js`) dibuja la evolución de ingresos y gastos,
    y la distribución de gastos por categoría en `panel.html`.

Los archivos vendor se consideran dependencias externas congeladas; no deben
editarse manualmente salvo que se actualice deliberadamente la versión de la
biblioteca.

## Recursos visuales (`static/assets`)

Los recursos visuales se sirven desde `app/static/assets/` y se organizan por
tipo para que las plantillas puedan referenciarlos mediante `/static/assets/...`:

- `img/`: logos de RDV Systems y FinovaTech, favicon, banners e imágenes de
    servicios como educación financiera, reportes, notificaciones y exportación.
- `icons/`: iconos auxiliares usados en elementos visuales de la interfaz.
- `video/`: `institucional.mp4`, utilizado como fondo o recurso audiovisual
    en las páginas que incluyen una presentación visual.

Los nombres de los archivos se mantienen como parte del contrato entre las
plantillas HTML y los estilos CSS. Si se reemplaza un recurso, debe conservarse
su ruta o actualizar simultáneamente todas las referencias que lo utilizan.

## Historial de versiones

Este historial resume la evolución funcional del sistema hasta la versión
actual:

| Versión | Hito principal |
|---|---|
| v1.0.0 | Estructura inicial del proyecto, página de inicio y navegación base. |
| v2.0.0 | Primeras pantallas de acceso: inicio de sesión y registro de usuarios. |
| v3.0.0 | Integración de Flask, configuración por entorno y conexión con MySQL. |
| v4.0.0 | Modelo de datos financiero con usuarios, estudiantes, ingresos y gastos. |
| v5.0.0 | Registro y eliminación de movimientos desde la lista financiera. |
| v6.0.0 | Panel con balance, totales, categorías, presupuesto y evolución mensual. |
| v7.0.0 | Agendamiento de sesiones, persistencia de citas y validaciones del formulario. |
| v8.0.0 | Notificaciones, páginas informativas, soporte y mejoras de navegación. |
| v9.0.0 | Seguridad de la aplicación: contraseñas cifradas, CSRF y control de acceso. |
| v10.0.0 | Consolidación de la documentación técnica del código, seguridad, páginas, assets y base de datos. |
| v10.1.0 | Mejora visual de las páginas públicas (portada, servicios y login): video de fondo, estadísticas reales, llamadas a la acción, entrada escalonada, botones pulsantes, barra de progreso de lectura y animaciones accesibles unificadas a la marca. |
| v10.2.0 | Validación en vivo de los formularios de login y registro: mensajes por campo, estados de error/acierto y animación de aviso, manteniendo la validación del servidor como fuente de verdad. |
| v10.3.0 | Mejora del panel: barra de progreso de lectura, entrada escalonada del sidebar y las tarjetas, soporte de `prefers-reduced-motion`, y corrección del desbordamiento horizontal entre 1025 y 1120px con ajuste de las tarjetas de estadísticas a dos columnas antes de que el monto se corte. |