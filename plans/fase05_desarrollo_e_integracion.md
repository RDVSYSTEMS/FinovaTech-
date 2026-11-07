# Fase 05 — Desarrollo e integración

## Objetivo

Mantener y completar la aplicación FinovaTech v10.3 (Flask + MySQL) dentro del
alcance ya definido, sin introducir funcionalidades fuera de los requisitos.

Fuentes de verdad (no duplicar aquí):
- Requisitos y rutas: `docs/REQUISITOS.md`.
- Modelo de datos: `docs/MODELO_DATOS.md`.
- Estructura, páginas y seguridad: `README.md`.

## Decisiones

- D1: Perfil MIDEGS **Estándar** (usuarios reales, persistencia, varias
  funcionalidades, sin requisitos regulatorios).
- D2: El entorno local usa MySQL/MariaDB de XAMPP en el puerto **3307**,
  porque el servicio `MySQL80` de Windows ocupa el 3306.
- D3: El puerto de MySQL se configura en `.env` (`DB_PORT`) y `iniciar.bat`
  lo lee de ahí; no se codifica en scripts.
- D4: Los planes 01–04 son retrospectivos y referencian `README.md` y `docs/`
  para no duplicar su contenido.

## Alcance

### Incluye

- Autenticación, roles y sesión.
- Registro de ingresos/gastos, presupuesto, notificaciones y agendamiento.
- Interfaz pública y panel, con animaciones accesibles.
- Endurecimiento de seguridad ya implementado (CSRF, cabeceras, bloqueo).

### No incluye

- Despliegue en producción, HTTPS real ni almacenamiento distribuido.
- Nuevos módulos no aprobados en `docs/REQUISITOS.md`.
- Cambios de stack o de arquitectura.

## Criterios de aceptación

- El servidor arranca y responde HTTP 200 en `http://localhost:5001`.
- La base `finovatech` conserva sus 8 tablas y la vista.
- Las rutas protegidas redirigen a `/login` sin sesión.
- No hay secretos en el código ni en Git.

## Riesgos

- R1: Dependencia de XAMPP y de un puerto no estándar (3307).
- R2: `.venv` atado a la ruta de Python de la máquina; si cambia, recrearlo.
- R3: Datos demo acumulados de smoke tests en la tabla `usuario`.

## Evidencia

- `.venv` recreado con Python 3.14.8 y dependencias instaladas.
- MariaDB 10.4.32 (XAMPP) en 3307 con `finovatech` y sus 8 tablas.
- `GET /` → HTTP 200 con el servidor en 5001.
- Cuenta demo validada: `adminr123@gmail.com` / `123456789`.
- Funcionalidades del alcance presentes en rutas y plantillas: login/registro,
  panel, lista, notificaciones y agendamiento.
- Suite de regresión en verde (detalle en `fase06_verificacion_validacion.md`).

## Iteración v10.3.4 — RF-13 Perfil de usuario

### Objetivo

Permitir que el usuario consulte sus datos y actualice nombre, nombre de usuario
y contraseña sin ampliar el resto del alcance.

### Alcance

- `GET/POST /perfil`: consulta y actualización de nombre/usuario.
- `POST /perfil/password`: cambio con verificación de la contraseña actual.
- Reutiliza CSRF, `login_requerido` y el hash de `werkzeug` ya existentes.
- No incluye edición de correo, rol ni recuperación de contraseña.

### Criterios de aceptación

- Los cambios persisten y se reflejan en la sesión y en `/perfil`.
- Un usuario duplicado o una contraseña actual incorrecta se rechazan.
- La nueva contraseña permite iniciar sesión.
- La suite smoke cubre los flujos anteriores.

### Evidencia

- `app/blueprints/perfil.py`, `app/templates/perfil.html` y
  `app/static/css/perfil.css` implementan la iteración.
- `tests/test_smoke.py` cubre datos, duplicados y cambio de contraseña.
- Suite completa: **25 comprobaciones OK** (`python -m tests.test_smoke`).
- Servidor real: login demo → `/perfil` 200; sin sesión → 302 a `/login`.

Estado: **cerrada** (2026-11-06) para v10.3.4; RF-13 verificado en fase 06.

## Iteración v10.3.6 - RF-15 a RF-18

### Objetivo

Completar los requisitos priorizados por el usuario: filtros/paginación en
servidor, supervisión del rol padre, bitácora de accesos y recuperación de
contraseña. RF-12 (reportes/CSV) sigue fuera de esta iteración.

### Decisiones

- D5: RF-16 usa un **código de vinculación** único generado para el estudiante;
  se evita vincular por correo para impedir que un padre consulte cuentas
  ajenas adivinando direcciones.
- D6: RF-18 usa SMTP por variables de entorno. Sin SMTP, el enlace se escribe
  en el log del servidor (modo local) y nunca en la respuesta HTTP.
- D7: RF-17 registra eventos en `bitacora_acceso` sin bloquear el login si la
  escritura de la bitácora falla.
- D8: RF-15 pagina de 10 en 10 y resuelve `q`/`tipo` en MySQL; el filtro
  JavaScript de la tabla deja de usarse en `/lista`.

### Alcance

- `/lista`: filtros GET, consulta paginada y controles de navegación.
- `/perfil`: muestra el código de vinculación del estudiante.
- `/supervision`, `/supervision/vincular`, `/supervision/desvincular/<id>`.
- `/bitacora` para administrador.
- `/recuperar` y `/restablecer/<token>`.
- Tablas `padre_estudiante`, `bitacora_acceso`, `recuperacion_password` y
  columna `estudiante.codigo_vinculacion`.
- No incluye RF-12, envío de correo en producción ni edición de datos del
  estudiante desde la vista del padre.

### Criterios de aceptación

- Los filtros y la paginación se resuelven en el servidor y conservan estado.
- Un padre solo ve estudiantes vinculados por código y puede desvincularlos.
- El administrador ve los eventos de acceso en `/bitacora`.
- Un token válido permite un único cambio de contraseña y caduca a los 30 min.
- `python -m tests.test_smoke` termina sin fallos con los nuevos flujos.

### Riesgos

- R4: Sin SMTP, el enlace de recuperación queda en el log; no sirve para
  usuarios finales hasta configurar el correo.
- R5: El código de vinculación debe compartirse por un canal seguro; si se
  filtra, permite que otro padre solicite supervisión de solo lectura.
- R6: Los tests crean cuentas y eventos adicionales en la base local.

### Evidencia

- Implementación: `app/blueprints/supervision.py`, `bitacora.py`,
  `recuperacion.py`; modelos equivalentes; plantillas `supervision.html`,
  `bitacora.html`, `recuperar.html` y `restablecer.html`.
- `app/modelos/finanzas.py` pagina y filtra en MySQL para RF-15; `/perfil`
  expone el código de vinculación.
- `scripts/seed_demo.py` carga 6 meses, 12 categorías, presupuesto al 117 %,
  notificaciones completas y la cuenta de padre vinculada.
- La portada calcula usuarios, movimientos y categorías reales desde MySQL.
- Suite ejecutada: **34 comprobaciones OK** (`python -m tests.test_smoke`),
  incluida la salida final `Todos los smoke tests v10 pasaron.`
- Datos demo restaurados después de la suite con
  `python -m scripts.seed_demo`.

Estado: **cerrada** (2026-11-06) para v10.3.6; RF-15 a RF-18 verificados en
fase 06.
