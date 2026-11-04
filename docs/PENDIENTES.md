# Pendientes — FinovaTech

Backlog vivo para la siguiente sesión. Fuente de verdad de requisitos:
`docs/REQUISITOS.md`. Historial de cambios: `docs/CHANGELOG.md`.

> **Recordatorio:** al retomar el proyecto, empezar por **RF-12 (reportes)**.
> Antes de codificar, actualizar `docs/REQUISITOS.md` y el plan de fase.

## Prioridad alta

- [ ] **RF-12 Reportes en la app + exportar CSV**
  - Ruta `/reportes` que use `sp_generar_reporte`, liste reportes y permita
    descargar CSV de movimientos.
  - Corregir `servicios.html`, que promete PDF/Excel/PNG no implementados.
  - Aceptación: generar un reporte, verlo listado y descargar el CSV.
- [ ] **RF-13 Perfil de usuario**
  - Ver/editar nombre y usuario; cambiar contraseña con verificación actual.
  - Aceptación: cambio persistido y login con la nueva contraseña.
- [ ] **RNF-10 Pruebas de escritura y anti fuerza bruta**
  - Crear/eliminar movimiento real y verificar bloqueo tras 5 intentos.
  - Aceptación: suite cubre ambos flujos sin mocks.

## Prioridad media

- [ ] **RF-14 Exportar movimientos (CSV)**
- [ ] **RF-15 Paginación y filtros en servidor** en `/lista`.
- [ ] **RF-16 Vista de supervisión para el rol padre** (hoy sin funciones).
- [ ] **RF-17 Bitácora de accesos** (login correcto/fallido, bloqueos).

## Prioridad baja

- [ ] **RNF-11 Usuario MySQL dedicado con contraseña** (dejar `root` solo para XAMPP).
- [ ] **RNF-12 Respaldo y restauración automatizados y probados**
  - Hoy existe `data/backups/finovatech_2026-11-03.sql`; falta probar la restauración.
- [ ] **RF-18 Recuperación de contraseña** (requiere definir envío de correo).

## Notas de estado

- Cuenta demo: `adminr123@gmail.com` / `123456789`.
- Presupuesto demo quedó en `$350.000` tras la prueba de `/presupuesto`.
- MySQL/MariaDB debe correr en `DB_PORT` (hoy `3307`).
- Suite actual: `python -m tests.test_smoke` → 23 comprobaciones.
