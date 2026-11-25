# Guion de presentación — FinovaTech v10.3.10

Duración objetivo: 15–18 minutos para el recorrido completo. Versión corta de
8 minutos: secciones 1, 4, 5, 7, 10 y 11. Demo en local con Opera.

## Antes de empezar (checklist)

1. MySQL de XAMPP activo en el puerto de `.env` (3306 en este equipo).
2. Servidor arriba: `.venv\Scripts\python.exe run.py` o `iniciar.bat`.
3. Abrir `http://localhost:5001` en Opera.
4. Tener a mano las cuentas demo:
   - Administrador/estudiante: `adminr123@gmail.com` / `123456789`
   - Padre vinculado: `padredemo@gmail.com` / `123456789`
5. Datos demo esperados: presupuesto `$600.000` con `$700.000` gastados
   (123 %), 6 meses de movimientos, 12 categorías y 6 notificaciones.
6. Respaldo previo de la base (opcional pero recomendado). Si hace falta
   restaurar: `python -m scripts.seed_demo`.

## Argumento en 30 segundos

- Problema: los estudiantes de bachillerato no ven en un solo lugar sus
  ingresos, gastos y el límite de gasto del mes.
- Solución: FinovaTech concentra movimientos, presupuesto, alertas, reportes
  y supervisión de un padre en una sola aplicación web.
- Diferenciadores: 17 RF numerados (RF-01 a RF-18, sin RF-11) más RF-02.1,
  12 RNF y 29 pruebas
  de integración contra MySQL real, PDF/PNG/CSV generados dentro de la app y
  bitácora de accesos.
- Impacto: el estudiante decide con datos reales y el padre acompaña en modo
  solo lectura, sin modificar la información.

## Recorrido sugerido

### 1. Portada (`/`) — 1 min

- Qué es FinovaTech y para quién (estudiantes de bachillerato).
- Estadísticas reales de usuarios, movimientos y categorías de gasto tomadas
  de la base.

### 2. Servicios y páginas informativas — 1 min

- `/servicios.html`: catálogo de servicios y llamada a la acción.
- Mencionar `/contacto.html`, `/soporte.html` y `/terminos.html`.

### 3. Registro (`/registro`) — 2 min

- Mostrar la validación en vivo por campo (error y acierto).
- Registrar un usuario de prueba con datos nuevos.
- Señalar que el rol administrador no se puede crear desde el formulario.

### 4. Login (`/login`) — 1 min

- Entrar con la cuenta demo.
- Mencionar CSRF, contraseñas cifradas y bloqueo por intentos fallidos.

### 5. Panel (`/panel`) — 3 min

- Ingresos, gastos, balance y movimientos recientes.
- Gráficas de evolución y distribución por categoría.
- Barra de presupuesto por estado.

### 6. Lista de movimientos (`/lista`) — 2 min

- Buscar por descripción y filtrar por tipo (los filtros se resuelven en MySQL).
- Recorrer la paginación de 10 en 10 conservando los filtros.
- Crear un ingreso o gasto y mostrarlo en la lista.
- Eliminar un movimiento propio.

### 7. Reportes, PDF y exportación (`/reportes`) — 2 min

- Totales del estudiante e historial de reportes generados.
- Generar un reporte en vivo (usa el stored procedure `sp_generar_reporte`).
- Abrir "Resumen mensual (PDF)": periodo, movimientos, ingresos, gastos y saldo.
- Mostrar el "Gráfico (PNG)" de gastos por categoría del mes.
- Descargar los movimientos en CSV; mencionar que abre en Excel o Google Sheets.

### 8. Notificaciones (`/notificacion`) — 1 min

- Alertas de presupuesto, gastos elevados y comportamiento mensual.

### 9. Agendamiento (`/agendamiento`) — 1 min

- Seleccionar fecha, hora, categoría, estado y comentarios.
- Enviar y confirmar el mensaje de resultado.

### 10. Supervisión del padre (`/supervision`) — 2 min

- Cerrar sesión e iniciar con `padredemo@gmail.com` / `123456789`.
- Mostrar el estudiante ya vinculado: totales, presupuesto y movimientos en
  solo lectura.
- Mencionar que la vinculación requiere el código que aparece en `/perfil` del
  estudiante y que el padre puede desvincular.

### 11. Seguridad y auditoría — 2 min

- `/bitacora` (solo administrador): login correcto, fallido, bloqueo, logout y
  recuperación.
- `/recuperar`: mensaje genérico; sin SMTP el enlace queda en el log local.
- CSRF en formularios, cookies HttpOnly, cabeceras, consultas parametrizadas y
  bloqueo tras 5 intentos.
- Cerrar sesión con el botón (POST con token).

## Cierre

- Resumen del alcance logrado: finanzas personales, presupuesto,
  notificaciones, agendamiento, supervisión del padre, bitácora y recuperación
   de contraseña. Aclarar lo que no incluye (producción, móvil, pagos).
- Cifra final para el jurado: 29/29 pruebas aprobadas y todos los RF
  documentados cubiertos por prueba o revisión.
- Preguntas.

## Preguntas probables del jurado

- **¿Por qué Flask y MySQL?** Son tecnologías instaladas en el colegio y
  permiten mostrar una aplicación real con persistencia, no una maqueta.
- **¿Cómo protegen los datos del usuario?** Contraseñas con hash, token CSRF
  en cada POST, cookies HttpOnly, cabeceras de seguridad y consultas
  parametrizadas; el bloqueo progresivo evita fuerza bruta.
- **¿Qué pasa si dos cuentas usan el mismo correo o el correo en mayúsculas?**
  El registro y el login normalizan el correo, y la base mantiene el correo
  y el usuario como columnas únicas.
- **¿Los reportes son exportaciones reales?** Sí: el PDF y el PNG se generan
  en servidor, el CSV sale de los movimientos del estudiante y el historial
  se guarda con un procedimiento almacenado.
- **¿Cómo demuestran que funciona?** La suite `pytest` ejecuta 29 casos
  contra MySQL real; la captura íntegra está en `entregable/`.
- **¿Qué harían con más tiempo?** Pruebas de navegador automatizadas, envío
  SMTP real y despliegue con HTTPS; están listados en `docs/PENDIENTES.md`.

## Evidencia lista para mostrar

- `entregable/captura_pytest_v.txt`: 29 pruebas aprobadas.
- `entregable/reporte_resumen_mensual.pdf`, `grafico_gastos.png` y
  `movimientos.csv`: salidas reales de la aplicación.
- `entregable/Bitacora_Arlant_Rafel.pdf`: bitácora de la actividad de pruebas.
- `docs/BITACORA_PRUEBAS.md`: matriz CP-01 a CP-06 y trazabilidad RF/RNF.

## Si algo falla

- MySQL no responde: revisar el puerto en `.env` y el panel de XAMPP.
- Login falla: verificar la cuenta demo y que la base tenga los datos semilla.
- Datos raros en la demo: recargar con `python -m scripts.seed_demo`.
