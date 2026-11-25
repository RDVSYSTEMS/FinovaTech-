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

- Suite de regresión: 29/29 casos OK (`pytest -v`).
- Arranque reproducible siguiendo solo el `README.md`.
- Documentación de fases 01–08 completa.

## Mejoras candidatas

Detalle, prioridades y criterios de aceptación en `docs/PENDIENTES.md`.

1. Completada en v10.3.5: flujos de escritura y bloqueo de login (RNF-10).
2. Completada en v10.3.6: filtros/paginación, supervisión del padre, bitácora y
   recuperación de contraseña (RF-15 a RF-18).
3. Completada en v10.3.8: restauración de respaldos probada y documentada
   (RNF-12).
4. Completada en v10.3.8: usuario MySQL dedicado `finovatech_app` (RNF-11).
5. Pendiente: pruebas de navegador automatizadas.
6. Completada en v10.3.8: reportes PDF y gráfico PNG, demostración en Colab.

## Riesgos

- R1: Mejoras que amplíen el alcance sin plan aprobado.
- R2: Deuda de pruebas fuera del smoke test.

## Evidencia

- Requisitos cubiertos según `docs/REQUISITOS.md` y la suite en verde.
- Lecciones registradas en `plans/fase05` y `plans/fase08`.
