# Fase 07 — Liberación y despliegue

## Objetivo

Preparar una entrega reproducible de FinovaTech v10.3 para la presentación del
proyecto de grado, sin desplegar en producción.

Referencias:
- Ejecución e instalación: `README.md`.
- Guion de demostración: `docs/GUION_PRESENTACION.md`.

## Decisiones

- D1: La liberación es local (XAMPP + Flask), no un despliegue en servidor.
- D2: La versión se marca con la etiqueta Git `v10.3.0`.
- D3: La entrega incluye código, `plans/`, `docs/` y datos demo; excluye
  `.env` y `.venv`.
- D4: El respaldo de la base se hace con `mysqldump` antes de la presentación.

## Alcance

### Incluye

- Etiqueta de versión sobre el commit de cierre.
- Verificación final de arranque y de la cuenta demo.
- Guion de presentación con recorrido por las páginas.

### No incluye

- Publicación en un hosting, HTTPS real o CI/CD.
- Empaquetado como ejecutable.

## Criterios de aceptación

- `git tag` muestra `v10.3.0` sobre el commit de cierre.
- El proyecto arranca siguiendo solo el `README.md`.
- La demo funciona con la cuenta `adminr123@gmail.com`.
- Existe respaldo de la base antes de la presentación.

## Riesgos

- R1: Otro equipo con el 3306 ocupado; usar `DB_PORT` en `.env`.
- R2: `.venv` no reproducible si cambia la ruta de Python.
- R3: Datos demo alterados por pruebas previas; recargar con `seed_demo`.

## Evidencia

- Etiqueta Git `v10.3.0` creada sobre el commit de cierre.
- Respaldo de la base: `data/backups/finovatech_2026-11-03.sql` (mysqldump con
  rutinas y triggers; 7 tablas y la vista).
- Arranque final verificado: `GET /` → HTTP 200 y cuenta demo operativa.
- Guion de presentación disponible en `docs/GUION_PRESENTACION.md`.
