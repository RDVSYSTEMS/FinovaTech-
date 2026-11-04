# Fase 08 — Operación y mantenimiento

## Objetivo

Mantener la aplicación operativa en el entorno local y dejar rutinas claras
para respaldos, recuperación y cambios menores.

Referencias:
- Instalación, ejecución y pruebas: `README.md`.
- Configuración por entorno: `.env.example`.
- Modelo y reglas de datos: `docs/MODELO_DATOS.md`.

## Decisiones

- D1: Operación local con XAMPP; el puerto de MySQL se toma de `DB_PORT`.
- D2: Respaldo con `mysqldump` en `data/backups/` (carpeta ignorada por Git).
- D3: Los datos demo se recargan con `scripts/seed_demo.py`, que es idempotente.
- D4: Cualquier cambio de esquema se aplica desde `database/schema.sql` y se
  refleja en `docs/MODELO_DATOS.md`.

## Alcance

### Incluye

- Arranque y parada del servidor y de MySQL.
- Respaldo y restauración de la base `finovatech`.
- Revisión de log del servidor y de la consola del navegador.
- Atención de incidentes frecuentes (puerto ocupado, login, datos demo).

### No incluye

- Monitoreo 24/7, alertas o alta disponibilidad.
- Actualizaciones automáticas de dependencias.

## Criterios de aceptación

- Existe un respaldo reciente y restaurable de la base.
- El proyecto arranca tras reiniciar el equipo siguiendo el `README.md`.
- Los incidentes frecuentes tienen un procedimiento documentado.

## Rutinas

- Antes de una presentación: respaldo + verificación de arranque + login demo.
- Tras cambios de código: ejecutar `python -m tests.test_smoke`.
- Al cambiar de equipo: recrear `.venv` y ajustar `.env`.

## Riesgos

- R1: Otro servicio ocupa el 3306; usar el puerto configurado en `.env`.
- R2: `.venv` no portable entre rutas de Python distintas.
- R3: Pérdida de datos si se restaura un respaldo antiguo por error.

## Evidencia

- Respaldo generado: `data/backups/finovatech_2026-11-03.sql`.
- Suite de regresión en verde (ver `fase06_verificacion_validacion.md`).
- Procedimientos de arranque y pruebas documentados en `README.md`.
