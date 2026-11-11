# Changelog — FinovaTech

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Las versiones anteriores están resumidas en el historial de `README.md`.

## [10.3.7] — 2026-11-10

### Añadido
- RF-12: `/reportes` con totales del estudiante, historial de reportes
  generados y generación vía `sp_generar_reporte` (tabla `reporte`).
- RF-14: `/exportar` descarga los movimientos del estudiante como CSV con BOM
  UTF-8 (abre en Excel y Google Sheets con tildes y eñes).
- Enlace "Reportes" en el menú lateral de las páginas autenticadas.
- Prueba `test_reportes_genera_y_exporta_csv` en la suite smoke.

### Cambiado
- `servicios.html` ya no promete exportación PDF/Excel/PNG: anuncia la
  exportación CSV real.
- Suite smoke ampliada a **37 comprobaciones**.

### Documentación
- `README.md`, `docs/REQUISITOS.md`, `docs/PENDIENTES.md` y
  `docs/GUION_PRESENTACION.md` actualizados a v10.3.7.

## [10.3.6] — 2026-11-06

### Añadido
- RF-15: filtros `q` y `tipo` en `/lista` resueltos en MySQL, paginación de 10
  en 10 y conservación de filtros al navegar.
- RF-16: código de vinculación en `/perfil`; `/supervision`,
  `/supervision/vincular` y `/supervision/desvincular/<id>` para el rol padre en
  modo solo lectura.
- RF-17: bitácora `bitacora_acceso` con login correcto/fallido, bloqueo, logout
  y recuperación; consulta restringida al administrador en `/bitacora`.
- RF-18: `/recuperar` y `/restablecer/<token>` con token de un solo uso, hash
  SHA-256, caducidad de 30 minutos y envío SMTP configurable por `.env`.
- Estadística real de categorías de gasto en la portada (`/`).
- Cuenta demo de padre vinculada al estudiante demo:
  `padredemo@gmail.com` / `123456789`.

### Cambiado
- `scripts/seed_demo.py`: 6 meses de datos (15 ingresos, 40 gastos y 12
  categorías), presupuesto `$600.000` con `$700.000` gastados (117 %), mes
  actual en negativo, gasto elevado y notificaciones completas.
- El enlace "Agendar" se retira del menú público; permanece en el menú
  autenticado.
- El pie de página indica "Desarrollado por RDV Systems para el SENA".
- Las barras de presupuesto limitan su ancho al 100 % aunque el porcentaje
  mostrado sea mayor.

### Documentación
- `README.md`, `docs/REQUISITOS.md`, `docs/MODELO_DATOS.md`,
  `docs/PENDIENTES.md`, `docs/GUION_PRESENTACION.md` y planes de las fases 05 y
  06 actualizados a v10.3.6.
- `.env.example` documenta `MAIL_*` y `PASSWORD_RESET_MINUTES`.
- Suite smoke ampliada a **34 comprobaciones** con RF-15, RF-16, RF-17 y RF-18.

## [10.3.5] — 2026-11-06

### Añadido
- RNF-10: prueba real de creación, persistencia y eliminación de un gasto,
  localizando el id desde el formulario de `/lista`.
- RNF-10: prueba de bloqueo del login tras cinco intentos fallidos, incluso
  con la contraseña correcta en el sexto intento.

### Documentación
- `docs/REQUISITOS.md` v10.3.5: RNF-10 y suite ampliada a **27 comprobaciones**.
- Plan de fase 06 y `docs/PENDIENTES.md` actualizados con la evidencia.

## [10.3.4] — 2026-11-06

### Añadido
- Página `/perfil` (GET/POST) para consultar la cuenta y actualizar nombre y
  nombre de usuario, con enlace en las barras laterales y el menú autenticado.
- Ruta `POST /perfil/password` para cambiar la contraseña verificando la actual.
- Plantilla `perfil.html`, estilos `perfil.css` y comprobación smoke del perfil.

### Corregido
- Servidor local reiniciado: un proceso Flask anterior seguía ocupando el puerto
  5001 con el código previo a RF-13 y provocaba 404 en `/perfil`.
- Navegación autenticada actualizada para incluir `/perfil` y `/presupuesto`.

### Documentación
- `docs/REQUISITOS.md` v10.3.4: RF-13, rutas de perfil y criterios 11–14.
- Suite smoke ampliada de 23 a **25 comprobaciones**.
- Planes de las fases 05 y 06 actualizados con la evidencia de RF-13.

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
