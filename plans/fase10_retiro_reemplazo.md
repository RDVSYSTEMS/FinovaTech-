# Fase 10 — Retiro o reemplazo

## Objetivo

Dejar definido cómo se retiraría o reemplazaría el sistema y qué se conserva,
sin ejecutar el retiro en esta entrega.

Referencias:
- Operación y respaldos: `plans/fase08_operacion_mantenimiento.md`.
- Ejecución y estructura: `README.md`.

## Decisiones

- D1: **No se retira** el sistema; la fase queda documentada como previsión.
- D2: El activo a conservar es el código versionado (Git + etiquetas) y la
  documentación de `plans/` y `docs/`.
- D3: Los datos se conservan mediante respaldo de la base antes de cualquier
  retiro o migración.

## Alcance

### Incluye

- Criterios para decidir el retiro o reemplazo.
- Pasos de cierre: respaldo final, exportación y archivo del repositorio.
- Traspaso de conocimiento (README, planes y guion).

### No incluye

- Migración a otro sistema ni eliminación de datos.

## Criterios para retirar o reemplazar

- El sistema deja de cumplir su propósito o es sustituido por otro aprobado.
- No hay usuarios activos ni obligación académica pendiente.
- Existe respaldo verificado y responsable del traspaso.

## Pasos de cierre (si se ejecutara)

1. Generar respaldo final con `mysqldump`.
2. Verificar la restauración en un entorno limpio.
3. Etiquetar la última versión y archivar el repositorio.
4. Entregar documentación y credenciales al responsable.
5. Dar de baja el entorno local (servidor y MySQL).

## Riesgos

- R1: Pérdida de datos por retiro sin respaldo verificado.
- R2: Dependencia de un entorno local no documentado.

## Evidencia

- Respaldo disponible: `data/backups/finovatech_2026-11-03.sql`.
- Repositorio versionado con etiquetas `v10.3.0` y `v10.3.1`.
- Documentación de fases 01–10 en `plans/`.
