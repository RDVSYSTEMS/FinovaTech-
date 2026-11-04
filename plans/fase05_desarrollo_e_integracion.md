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

Estado: **cerrada** (2026-11-03).
