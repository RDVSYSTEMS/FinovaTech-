# Fase 04 — Planificación y preparación

> Documento retrospectivo (reconstruido el 2026-11-03). Los comandos de
> instalación y ejecución vigentes están en `README.md`.

## Objetivo

Preparar el entorno, el orden de trabajo y los criterios de verificación antes
de implementar.

## Decisiones

- D1: Entorno local con Python 3.14, `.venv` y XAMPP (MySQL/MariaDB).
- D2: Configuración por `.env` (`DB_HOST`, `DB_PORT`, `DB_USER`,
  `DB_PASSWORD`, `DB_NAME`, `SECRET_KEY`); `.env` no se versiona.
- D3: Orden de construcción por hitos funcionales (v1 a v10) y verificación
  con `tests/test_smoke.py`.
- D4: Datos de demostración repetibles con `scripts/seed_demo.py`.

## Alcance

### Incluye

- Creación del entorno virtual e instalación de dependencias.
- Creación y carga del esquema en MySQL.
- Definición de la estrategia de pruebas y de la cuenta demo.

### No incluye

- Automatización de despliegue o integración continua.

## Criterios de aceptación

- El entorno se reproduce siguiendo solo el `README.md`.
- La base de datos se crea desde `database/schema.sql`.
- Existe una cuenta demo para pruebas y presentación.

## Riesgos

- R1: `.venv` atado a la ruta de Python de la máquina; debe recrearse si cambia.
- R2: Conflicto de puerto si otro servicio ocupa el 3306 (se resuelve con
  `DB_PORT` en `.env`).

## Evidencia

- `requirements.txt` con Flask, Flask-CORS, PyMySQL y python-dotenv.
- `iniciar.bat` valida el entorno y el puerto de MySQL antes de arrancar.
- `scripts/seed_demo.py` carga datos de demostración de forma idempotente.
