# Fase 09 — Evaluación y mejora

## Objetivo

Valorar el resultado de v10.3 frente a los requisitos y registrar mejoras
candidatas, sin ampliar el alcance de la entrega actual.

Referencias:
- Requisitos y criterios: `docs/REQUISITOS.md`.
- Verificación: `plans/fase06_verificacion_validacion.md`.

## Decisiones

- D1: La evaluación se basa en evidencia ya obtenida (suite, demo y revisión
  manual), no en métricas nuevas.
- D2: Las mejoras se registran como candidatas; no se implementan en esta fase.
- D3: Se prioriza lo que aporte a la presentación y a la estabilidad local.

## Alcance

### Incluye

- Contraste entre requisitos y funcionalidad entregada.
- Lecciones aprendidas del entorno (puertos, `.venv`, datos demo).
- Lista priorizada de mejoras futuras.

### No incluye

- Rediseño, cambios de stack ni nuevas funcionalidades.

## Indicadores

- Suite de regresión: 15/15 comprobaciones OK.
- Arranque reproducible siguiendo solo el `README.md`.
- Documentación de fases 01–08 completa.

## Mejoras candidatas

1. Pruebas automatizadas de presupuesto, notificaciones y agendamiento.
2. Restauración de respaldos probada y documentada.
3. Contraseña de MySQL distinta de la de por defecto.
4. Pruebas de navegador automatizadas.

## Riesgos

- R1: Mejoras que amplíen el alcance sin plan aprobado.
- R2: Deuda de pruebas fuera del smoke test.

## Evidencia

- Requisitos cubiertos según `docs/REQUISITOS.md` y la suite en verde.
- Lecciones registradas en `plans/fase05` y `plans/fase08`.
