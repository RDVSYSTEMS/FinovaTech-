# Fase 07 — Liberación y despliegue

## Objetivo

Preparar una entrega reproducible de FinovaTech v10.3 para la presentación del
proyecto de grado, sin desplegar en producción.

Referencias:
- Ejecución e instalación: `README.md`.
- Guion de demostración: `docs/GUION_PRESENTACION.md`.

## Decisiones

- D1: La liberación es local (XAMPP + Flask), no un despliegue en servidor.
- D2: La versión se marca con la etiqueta Git `v10.3.8`.
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

- `git tag` muestra `v10.3.8` sobre el commit de cierre.
- El proyecto arranca siguiendo solo el `README.md`.
- La demo funciona con las cuentas `adminr123@gmail.com` y
  `padredemo@gmail.com`.
- Existe respaldo de la base antes de la presentación.

## Riesgos

- R1: Otro equipo con el 3306 ocupado; usar `DB_PORT` en `.env`.
- R2: `.venv` no reproducible si cambia la ruta de Python.
- R3: Datos demo alterados por pruebas previas; recargar con `seed_demo`.

## Evidencia

- Etiqueta Git `v10.3.8` creada sobre el commit de cierre.
- Respaldo vigente: `data/backups/finovatech_2026-11-18.sql` (mysqldump con
  rutinas y triggers; 11 tablas, 1 vista, 4 rutinas y 4 triggers). Restauración
  probada en `finovatech_restore_test`.
- Arranque final verificado: `GET /` → HTTP 200 y cuentas demo operativas.
- Suite de regresión: 28 pruebas en verde (`pytest -v`).
- Guion de presentación disponible en `docs/GUION_PRESENTACION.md`.
- Entrega para Google Colab: `colab/FinovaTech_Colab.ipynb`.
