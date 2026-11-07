# Guion de presentación — FinovaTech v10.3.6

Duración objetivo: 10–15 minutos. Demo en local con Opera.

## Antes de empezar (checklist)

1. MySQL de XAMPP activo en el puerto de `.env` (3307 en este equipo).
2. Servidor arriba: `.venv\Scripts\python.exe run.py` o `iniciar.bat`.
3. Abrir `http://localhost:5001` en Opera.
4. Tener a mano las cuentas demo:
   - Administrador/estudiante: `adminr123@gmail.com` / `123456789`
   - Padre vinculado: `padredemo@gmail.com` / `123456789`
5. Datos demo esperados: presupuesto `$600.000` con `$700.000` gastados
   (117 %), 6 meses de movimientos, 12 categorías y 6 notificaciones.
6. Respaldo previo de la base (opcional pero recomendado). Si hace falta
   restaurar: `python -m scripts.seed_demo`.

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

### 7. Notificaciones (`/notificacion`) — 1 min

- Alertas de presupuesto, gastos elevados y comportamiento mensual.

### 8. Agendamiento (`/agendamiento`) — 1 min

- Seleccionar fecha, hora, categoría, estado y comentarios.
- Enviar y confirmar el mensaje de resultado.

### 9. Supervisión del padre (`/supervision`) — 2 min

- Cerrar sesión e iniciar con `padredemo@gmail.com` / `123456789`.
- Mostrar el estudiante ya vinculado: totales, presupuesto y movimientos en
  solo lectura.
- Mencionar que la vinculación requiere el código que aparece en `/perfil` del
  estudiante y que el padre puede desvincular.

### 10. Seguridad y auditoría — 2 min

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
- Preguntas.

## Si algo falla

- MySQL no responde: revisar el puerto en `.env` y el panel de XAMPP.
- Login falla: verificar la cuenta demo y que la base tenga los datos semilla.
- Datos raros en la demo: recargar con `python -m scripts.seed_demo`.
