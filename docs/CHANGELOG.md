# Changelog — FinovaTech

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Las versiones anteriores están resumidas en el historial de `README.md`.

## [10.3.3] — 2026-11-04

### Añadido
- Página `/presupuesto` (GET/POST) para definir o actualizar el límite de gasto
  del mes vigente, con validación de monto positivo y máximo permitido.
- Enlaces a presupuesto desde el panel, la lista y las notificaciones.
- `docs/PENDIENTES.md`: backlog priorizado de requisitos pendientes.
- Comprobación smoke de definición y validación del presupuesto.

### Corregido
- Tabla `agendamiento` ausente en la base de datos local: reaplicado
  `database/schema.sql` (idempotente) y verificado con un alta/baja real.
- Suite smoke ampliada de 21 a 23 comprobaciones.

### Documentación
- `docs/REQUISITOS.md` v10.3.3: RF-06 editable, ruta `/presupuesto`,
  Python 3.14 y puerto configurable con `DB_PORT`.
- `plans/fase02`, `fase06` y `fase09` actualizados con el nuevo alcance.

## [10.3.2] — 2026-11-03

- Suite ampliada a presupuesto, notificaciones y validación del agendamiento.
- Planes de las fases 09 y 10.

## [10.3.1] — 2026-11-03

- Documentación MIDEGS de las fases 01–08, planes de fase y guion de presentación.

## [10.3.0] — 2026-11-03

- Mejora del panel: barra de progreso, entrada escalonada, `prefers-reduced-motion`
  y corrección del desbordamiento horizontal entre 1025 y 1120 px.
