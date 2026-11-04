# Fase 03 — Arquitectura y diseño

> Documento retrospectivo (reconstruido el 2026-11-03). La arquitectura y el
> modelo de datos están definidos en `docs/MODELO_DATOS.md` y `README.md`.

## Objetivo

Definir una arquitectura suficiente para el alcance, sin complejidad
innecesaria, y el modelo de datos que la soporta.

## Decisiones

- D1: Flask con patrón factory (`create_app`) y blueprints por responsabilidad:
  `publicas`, `panel`, `registros`, `notificaciones`.
- D2: Acceso a datos con PyMySQL y SQL parametrizado; nombres de tabla desde
  lista blanca.
- D3: Separación en capas: blueprints (rutas), modelos (consultas), plantillas
  Jinja y estáticos.
- D4: La base de datos concentra integridad con claves foráneas, triggers,
  procedimientos y una vista de resumen.

## Alcance

### Incluye

- Estructura de carpetas, capas y responsabilidades.
- Modelo entidad-relación, tablas, claves y reglas de persistencia.
- Seguridad desde el diseño (CSRF, sesiones, cabeceras).

### No incluye

- Microservicios, colas, caché distribuida o contenedores.

## Criterios de aceptación

- Cada capa tiene una responsabilidad clara y sin duplicación.
- El modelo de datos cubre todos los requisitos funcionales.
- No hay SQL concatenado con datos del usuario.

## Riesgos

- R1: Acoplamiento entre rutas y consultas si crece el alcance.
- R2: Reglas de negocio repartidas entre aplicación y base de datos.

## Evidencia

- `docs/MODELO_DATOS.md`: ER v10, tablas, triggers, procedures y vista.
- `database/schema.sql`: 8 tablas, relaciones y vista de resumen.
- `README.md`: estructura del proyecto y descripción de capas.
