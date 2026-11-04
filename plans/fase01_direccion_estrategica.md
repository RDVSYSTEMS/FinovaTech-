# Fase 01 — Dirección estratégica y viabilidad

> Documento retrospectivo (reconstruido el 2026-11-03). No repite información
> ya presente en `README.md`.

## Objetivo

Definir el propósito del proyecto y comprobar que era viable construirlo con
los recursos disponibles.

## Decisiones

- D1: Producto: sistema web de finanzas personales para estudiantes de
  bachillerato, como proyecto de grado SENA de RDV Systems.
- D2: Alcance académico y local; no comercial en esta etapa.
- D3: Stack de bajo costo y ya disponible: Flask, MySQL/MariaDB (XAMPP),
  HTML/CSS/JS sin framework de frontend.
- D4: Se descarta autenticación externa, pagos y aplicación móvil nativa.

## Alcance

### Incluye

- Gestión de ingresos, gastos, presupuesto y notificaciones.
- Agendamiento de sesiones de acompañamiento.
- Uso local con datos de demostración.

### No incluye

- Infraestructura en la nube, alta disponibilidad o multiusuario masivo.
- Integraciones bancarias o pasarelas de pago.

## Criterios de aceptación

- El proyecto se ejecuta en un equipo con Python y XAMPP.
- El alcance cabe en el tiempo disponible del proyecto de grado.

## Riesgos

- R1: Dependencia de XAMPP y de configuración manual de la base de datos.
- R2: Alcance creciente sin control de cambios.

## Evidencia

- Objetivo y stack descritos en `README.md` (v1.0.0 en el historial).
- Estructura inicial del repositorio y navegación base.
