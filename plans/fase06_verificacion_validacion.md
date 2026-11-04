# Fase 06 — Verificación y validación

## Objetivo

Comprobar que lo construido cumple los requisitos y funciona de extremo a
extremo en el entorno local, con evidencia reproducible.

Referencias:
- Requisitos y criterios: `docs/REQUISITOS.md`.
- Instrucciones de ejecución y pruebas: `README.md`.

## Decisiones

- D1: La suite existente (`tests/test_smoke.py`) es la base de regresión.
- D2: La verificación requiere MySQL activo y el esquema aplicado.
- D3: Los fallos encontrados se corrigen en Fase 05 antes de cerrar esta fase.

## Alcance

### Incluye

- Smoke tests de rutas públicas, login, rutas protegidas y CSRF.
- Prueba manual de los flujos principales en navegador:
  registro, login, panel, lista, notificaciones y agendamiento.
- Revisión de consola del navegador y de errores del servidor.

### No incluye

- Pruebas de carga o de penetración.
- Pruebas automatizadas de navegador (no hay framework instalado).
- Validación en producción.

## Criterios de aceptación

- `python -m tests.test_smoke` termina sin fallos.
- Login demo y acceso al panel funcionan en Opera.
- Un POST sin `csrf_token` se rechaza con HTTP 400.
- Sin errores en la consola del navegador en las páginas principales.
- Cada requisito verificado queda con evidencia registrada en este plan.

## Riesgos

- R1: Los smoke tests crean usuarios de prueba en la base local.
- R2: Diferencias de comportamiento entre navegadores no cubiertas.
- R3: Resultados dependientes del puerto de MySQL configurado en `.env`.

## Evidencia

- Pendiente de ejecutar en esta fase: resultados de la suite y de la revisión
  manual se anexan aquí al cierre.
