# Pendientes — FinovaTech

Backlog vivo para la siguiente sesión. Fuente de verdad de requisitos:
`docs/REQUISITOS.md`. Historial de cambios: `docs/CHANGELOG.md`.

> **Recordatorio:** al retomar el proyecto, seguir por **RF-14** (exportar
> movimientos en CSV). **RF-12 queda fuera de esta iteración** por decisión del
> usuario. Antes de codificar, actualizar `docs/REQUISITOS.md` y el plan de fase.

## Prioridad alta

- [ ] **RF-12 Reportes en la app + exportar CSV**
  - Ruta `/reportes` que use `sp_generar_reporte`, liste reportes y permita
    descargar CSV de movimientos.
  - Corregir `servicios.html`, que promete PDF/Excel/PNG no implementados.
  - Aceptación: generar un reporte, verlo listado y descargar el CSV.
- [x] **RF-13 Perfil de usuario** — cerrado 2026-11-06
  - Ver/editar nombre y usuario; cambiar contraseña con verificación actual.
  - Aceptación: cambio persistido, rechazo de duplicados y login con la nueva
    contraseña. Evidencia en `docs/CHANGELOG.md` y `plans/fase06`.
- [x] **RNF-10 Pruebas de escritura y anti fuerza bruta** — cerrado 2026-11-06
  - Crear/eliminar movimiento real y verificar bloqueo tras 5 intentos.
  - Aceptación: suite cubre ambos flujos sin mocks. Evidencia en
    `docs/CHANGELOG.md` y `plans/fase06`.

## Prioridad media

- [ ] **RF-14 Exportar movimientos (CSV)**
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

- [ ] **RNF-11 Usuario MySQL dedicado con contraseña** (dejar `root` solo para XAMPP).
- [ ] **RNF-12 Respaldo y restauración automatizados y probados**
  - Hoy existe `data/backups/finovatech_2026-11-03.sql`; falta probar la restauración.

## Notas de estado

- Cuenta demo administrador/estudiante: `adminr123@gmail.com` / `123456789`.
- Cuenta demo padre vinculada: `padredemo@gmail.com` / `123456789`.
- Presupuesto demo: `$600.000` límite, `$700.000` gastado (117 %).
- MySQL/MariaDB debe correr en `DB_PORT` (hoy `3307`).
- Suite actual: `python -m tests.test_smoke` → **34 comprobaciones**.
- Tras ejecutar la suite, restaurar datos con
  `python -m scripts.seed_demo` (la prueba de presupuesto modifica el demo).
- RF-13, RNF-10 y RF-15 a RF-18 cerrados; siguiente requisito priorizado: RF-14.
