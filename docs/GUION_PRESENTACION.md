# Guion de presentación — FinovaTech v10.3

Duración objetivo: 10–15 minutos. Demo en local con Opera.

## Antes de empezar (checklist)

1. MySQL de XAMPP activo en el puerto de `.env` (3307 en este equipo).
2. Servidor arriba: `.venv\Scripts\python.exe run.py` o `iniciar.bat`.
3. Abrir `http://localhost:5001` en Opera.
4. Tener a mano la cuenta demo:
   - Correo: `adminr123@gmail.com`
   - Contraseña: `123456789`
5. Respaldo previo de la base (opcional pero recomendado).

## Recorrido sugerido

### 1. Portada (`/`) — 1 min

- Qué es FinovaTech y para quién (estudiantes de bachillerato).
- Estadísticas reales de usuarios y movimientos tomadas de la base.

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

- Buscar y filtrar.
- Crear un ingreso o gasto y mostrarlo en la lista.
- Eliminar un movimiento propio.

### 7. Notificaciones (`/notificacion`) — 1 min

- Alertas de presupuesto, gastos elevados y comportamiento mensual.

### 8. Agendamiento (`/agendamiento`) — 1 min

- Seleccionar fecha, hora, categoría, estado y comentarios.
- Enviar y confirmar el mensaje de resultado.

### 9. Seguridad — 1 min

- CSRF en formularios, cookies HttpOnly, cabeceras y consultas parametrizadas.
- Cerrar sesión con el botón (POST con token).

## Cierre

- Resumen del alcance logrado y de lo que no incluye (producción, móvil, pagos).
- Preguntas.

## Si algo falla

- MySQL no responde: revisar el puerto en `.env` y el panel de XAMPP.
- Login falla: verificar la cuenta demo y que la base tenga los datos semilla.
- Datos raros en la demo: recargar con `python -m scripts.seed_demo`.
