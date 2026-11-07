# Fase 02 — Descubrimiento y requisitos

> Documento retrospectivo (reconstruido el 2026-11-03). La fuente de verdad de
> requisitos es `docs/REQUISITOS.md`; aquí solo se registran las decisiones.

## Objetivo

Identificar necesidades de los estudiantes y convertirlas en requisitos
funcionales y no funcionales verificables.

## Decisiones

- D1: Los requisitos funcionales y no funcionales, rutas y criterios se
  documentan en `docs/REQUISITOS.md`.
- D2: Roles del sistema: estudiante, padre y administrador.
- D3: El registro público solo permite estudiante y padre; el administrador
  se crea por datos semilla.
- D4: La validación del servidor es la fuente de verdad; la del cliente es
  apoyo visual.

## Alcance

### Incluye

- Autenticación, movimientos, presupuesto, notificaciones y agendamiento.
- Presupuesto editable desde la app (RF-06), no solo de lectura.
- Perfil de usuario editable (RF-13): nombre, usuario y contraseña.
- Requisitos de seguridad: CSRF, contraseñas cifradas, control de acceso.

### No incluye

- Requisitos regulatorios, auditoría formal o cumplimiento normativo.

## Criterios de aceptación

- Cada funcionalidad implementada se puede rastrear a un requisito.
- Los requisitos no funcionales tienen criterio comprobable.

## Riesgos

- R1: Requisitos ambiguos que generen retrabajo.
- R2: Cambios de alcance sin actualizar el documento de requisitos.

## Evidencia

- `docs/REQUISITOS.md` (SRS v10) con RF, RNF y criterios.
- Rutas y contrato del agendamiento documentados en el mismo archivo.
