# Pendientes — FinovaTech

Backlog vivo para la siguiente sesión. Fuente de verdad de requisitos:
`docs/REQUISITOS.md`. Historial de cambios: `docs/CHANGELOG.md`.

> **Recordatorio:** RNF-11 y RNF-12 se cerraron el 2026-11-18. No quedan
> requisitos funcionales ni no funcionales abiertos; las siguientes mejoras
> son las candidatas de la fase 09 (pruebas de navegador, SMTP real).

## Prioridad alta

- [x] **RF-12 Reportes en la app + exportar CSV** — cerrado 2026-11-10
  - Ruta `/reportes` que usa `sp_generar_reporte`, lista reportes y permite
    descargar CSV de movimientos.
  - Corregido `servicios.html`, que prometía PDF/Excel/PNG no implementados.
  - Aceptación: generar un reporte, verlo listado y descargar el CSV.
  - Evidencia: prueba `test_reportes_genera_y_exporta_csv` en la suite smoke.
- [x] **RF-13 Perfil de usuario** — cerrado 2026-11-06
  - Ver/editar nombre y usuario; cambiar contraseña con verificación actual.
  - Aceptación: cambio persistido, rechazo de duplicados y login con la nueva
    contraseña. Evidencia en `docs/CHANGELOG.md` y `plans/fase06`.
- [x] **RNF-10 Pruebas de escritura y anti fuerza bruta** — cerrado 2026-11-06
  - Crear/eliminar movimiento real y verificar bloqueo tras 5 intentos.
  - Aceptación: suite cubre ambos flujos sin mocks. Evidencia en
    `docs/CHANGELOG.md` y `plans/fase06`.

## Prioridad media

- [x] **RF-14 Exportar movimientos (CSV)** — cerrado 2026-11-10
  - `/exportar` descarga los movimientos del estudiante como CSV con BOM UTF-8.
  - Evidencia: prueba `test_reportes_genera_y_exporta_csv` en la suite smoke.
- [x] **RF-15 Paginación y filtros en servidor** — cerrado 2026-11-06
  - `/lista` resuelve `q`/`tipo` en MySQL, pagina de 10 en 10 y conserva filtros.
  - Evidencia: prueba `test_lista_filtros_y_paginacion` en la suite smoke.
- [x] **RF-16 Vista de supervisión para el rol padre** — cerrado 2026-11-06
  - Vinculación por código, consulta en solo lectura y desvinculación.
  - Evidencia: `test_supervision_padre_vincula_y_desvincula`.
- [x] **RF-17 Bitácora de accesos** — cerrado 2026-11-06
  - Login correcto/fallido, bloqueo, logout y recuperación; solo administrador.
  - Evidencia: `test_bitacora_accesos_admin`.
- [x] **RF-18 Recuperación de contraseña** — cerrado 2026-11-06
  - Token de un solo uso con caducidad de 30 minutos y SMTP por entorno.
  - Evidencia: `test_recuperacion_password_token_un_uso`.

## Prioridad baja

- [x] **RNF-11 Usuario MySQL dedicado con contraseña** — cerrado 2026-11-18
  - Usuario `finovatech_app` con permisos solo sobre `finovatech`; `.env` y
    `.env.example` actualizados; la suite pasa con ese usuario.
- [x] **RNF-12 Respaldo y restauración automatizados y probados** — cerrado 2026-11-18
  - Respaldo `data/backups/finovatech_2026-11-18.sql` (rutinas y triggers).
  - Restauración verificada en `finovatech_restore_test`: 11 tablas, 1 vista,
    4 rutinas, 4 triggers y los mismos registros; base temporal eliminada.
  - Procedimiento documentado en `README.md`.

## Notas de estado

- Cuenta demo administrador/estudiante: `adminr123@gmail.com` / `123456789`.
- Cuenta demo padre vinculada: `padredemo@gmail.com` / `123456789`.
- Presupuesto demo: `$600.000` límite, `$700.000` gastado (117 %).
- MySQL/MariaDB debe correr en `DB_PORT` (hoy `3306`; la guía menciona 3307).
- Suite actual: `python -m pytest -v` → **28 casos** en
  `tests/test_finovatech.py` (22 del flujo general + CP-01 a CP-06).
- Tras ejecutar la suite, restaurar datos con
  `python -m scripts.seed_demo` (la prueba de presupuesto modifica el demo).
- RF-12 a RF-18, RF-13, RNF-10, RNF-11 y RNF-12 cerrados; solo quedan mejoras
  candidatas (pruebas de navegador y SMTP real).
