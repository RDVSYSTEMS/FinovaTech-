# Guía de archivos y módulos de FinovaTech

Este índice complementa la documentación que ya está dentro del código: los módulos Python describen su responsabilidad en el docstring inicial y las vistas, estilos, JavaScript y SQL usan comentarios de encabezado o de sección. Los módulos de terceros minificados de `app/static/vendor/` y los recursos binarios de `app/static/assets/` se dejan intactos para preservar sus licencias y archivos originales.

## Inicio y configuración

- [run.py](../run.py): crea la aplicación Flask y arranca el servidor local con el puerto y modo de depuración configurados.
- [iniciar.bat](../iniciar.bat): lanzador de Windows; verifica el puerto de MySQL y abre la aplicación.
- [requirements.txt](../requirements.txt): dependencias Python fijadas para instalar el proyecto.
- [app/**init**.py](../app/__init__.py): fábrica Flask, registro de blueprints y conexión de las protecciones globales.
- [app/config.py](../app/config.py): configuración de base de datos, sesión, SMTP y recuperación desde variables de entorno.
- [app/db.py](../app/db.py): creación de conexiones PyMySQL con filas tipo diccionario.
- [app/correo.py](../app/correo.py): envío SMTP del enlace para restablecer contraseña y alternativa de log en desarrollo.
- [app/seguridad.py](../app/seguridad.py): CSRF, control de sesión y roles, bloqueo progresivo de login y cabeceras HTTP.

## Rutas HTTP: blueprints

- [app/blueprints/**init**.py](../app/blueprints/__init__.py): paquete que agrupa los módulos de rutas.
- [app/blueprints/publicas.py](../app/blueprints/publicas.py): inicio, login, registro, cierre de sesión y alias de páginas públicas.
- [app/blueprints/panel.py](../app/blueprints/panel.py): dashboard autenticado y edición del presupuesto mensual.
- [app/blueprints/registros.py](../app/blueprints/registros.py): lista de movimientos, filtros, paginación, alta y eliminación.
- [app/blueprints/notificaciones.py](../app/blueprints/notificaciones.py): centro de notificaciones y endpoint de agendamiento.
- [app/blueprints/perfil.py](../app/blueprints/perfil.py): consulta y actualización de perfil y contraseña.
- [app/blueprints/supervision.py](../app/blueprints/supervision.py): vinculación de cuentas y supervisión de solo lectura para el rol padre.
- [app/blueprints/bitacora.py](../app/blueprints/bitacora.py): consulta administrativa de eventos de acceso.
- [app/blueprints/recuperacion.py](../app/blueprints/recuperacion.py): solicitud de restablecimiento y validación del enlace de un solo uso.

## Acceso a datos: modelos

- [app/modelos/**init**.py](../app/modelos/__init__.py): paquete de modelos de dominio.
- [app/modelos/usuarios.py](../app/modelos/usuarios.py): registro, autenticación, consulta y cambios de datos de usuario.
- [app/modelos/finanzas.py](../app/modelos/finanzas.py): consultas del panel, movimientos, presupuesto, paginación y avisos financieros.
- [app/modelos/agendamientos.py](../app/modelos/agendamientos.py): validación y persistencia de sesiones de educación financiera.
- [app/modelos/supervision.py](../app/modelos/supervision.py): códigos de vinculación y relaciones padre-estudiante.
- [app/modelos/bitacora.py](../app/modelos/bitacora.py): registro y lectura de eventos de autenticación.
- [app/modelos/recuperacion.py](../app/modelos/recuperacion.py): generación, hash, validación y consumo de tokens de recuperación.

## Plantillas HTML/Jinja

- [app/templates/index.html](../app/templates/index.html): portada, estadísticas y presentación del servicio.
- [app/templates/servicios.html](../app/templates/servicios.html): catálogo informativo de funciones.
- [app/templates/contacto.html](../app/templates/contacto.html): datos de contacto y créditos.
- [app/templates/soporte.html](../app/templates/soporte.html): ayuda y formulario de soporte.
- [app/templates/terminos.html](../app/templates/terminos.html): términos y condiciones.
- [app/templates/login.html](../app/templates/login.html): formulario de autenticación y validación de campos.
- [app/templates/registro.html](../app/templates/registro.html): creación de cuentas de estudiante o padre.
- [app/templates/recuperar.html](../app/templates/recuperar.html): solicitud de enlace de recuperación.
- [app/templates/restablecer.html](../app/templates/restablecer.html): formulario para establecer una contraseña con token válido.
- [app/templates/panel.html](../app/templates/panel.html): resumen financiero, gráficos y alta rápida de movimientos.
- [app/templates/lista.html](../app/templates/lista.html): historial, filtros, paginación y formularios de movimiento.
- [app/templates/presupuesto.html](../app/templates/presupuesto.html): definición y seguimiento del límite mensual.
- [app/templates/agendamiento.html](../app/templates/agendamiento.html): formulario de reserva de sesión financiera.
- [app/templates/notificacion.html](../app/templates/notificacion.html): avisos financieros y recordatorios.
- [app/templates/perfil.html](../app/templates/perfil.html): datos de cuenta, código de vínculo y cambio de contraseña.
- [app/templates/supervision.html](../app/templates/supervision.html): resumen de estudiantes asociados a la cuenta padre.
- [app/templates/bitacora.html](../app/templates/bitacora.html): tabla de eventos accesible para administradores.

## Frontend: JavaScript y estilos

- [app/static/js/global.js](../app/static/js/global.js): comportamiento compartido, navegación, componentes móviles, formularios y utilidades de interfaz.
- [app/static/css/header_footer.css](../app/static/css/header_footer.css): estilos globales del encabezado, navegación y pie de página.
- [app/static/css/index.css](../app/static/css/index.css): composición visual de la portada y sus secciones.
- [app/static/css/servicios.css](../app/static/css/servicios.css): presentación de tarjetas y contenido de servicios.
- [app/static/css/contacto.css](../app/static/css/contacto.css): diseño de la página de contacto.
- [app/static/css/soporte.css](../app/static/css/soporte.css): formulario y estados visuales de soporte.
- [app/static/css/terminos.css](../app/static/css/terminos.css): lectura y estructura visual de los términos.
- [app/static/css/login.css](../app/static/css/login.css): pantalla y formulario de inicio de sesión.
- [app/static/css/registro.css](../app/static/css/registro.css): pantalla y formulario de registro.
- [app/static/css/panel.css](../app/static/css/panel.css): estructura común del panel, navegación lateral y componentes.
- [app/static/css/lista.css](../app/static/css/lista.css): tabla, filtros, paginación y formularios de movimientos.
- [app/static/css/presupuesto.css](../app/static/css/presupuesto.css): visualización y edición del presupuesto.
- [app/static/css/agendamiento.css](../app/static/css/agendamiento.css): contenido y formulario de reserva de sesiones.
- [app/static/css/notificacion.css](../app/static/css/notificacion.css): tarjetas y estados del centro de notificaciones.
- [app/static/css/perfil.css](../app/static/css/perfil.css): formularios y datos del perfil.
- [app/static/css/supervision.css](../app/static/css/supervision.css): resumen de estudiantes vinculados.
- [app/static/css/bitacora.css](../app/static/css/bitacora.css): tabla de auditoría de accesos.

### Bibliotecas de terceros

Se documentan aquí como dependencias frontend, pero no se editan ni se insertan comentarios dentro de sus bundles originales.

- [app/static/vendor/aos.js](../app/static/vendor/aos.js) y [app/static/vendor/aos.css](../app/static/vendor/aos.css): biblioteca Animate On Scroll y sus estilos.
- [app/static/vendor/chart.umd.min.js](../app/static/vendor/chart.umd.min.js): bundle minificado de Chart.js usado por los gráficos del panel.

## Base de datos, datos demo y pruebas

- [database/schema.sql](../database/schema.sql): crea las tablas, claves, vista, triggers y procedimientos almacenados del sistema.
- [scripts/seed_demo.py](../scripts/seed_demo.py): prepara cuentas y movimientos reproducibles para una demostración local.
- [tests/test_smoke.py](../tests/test_smoke.py): verifica rutas, sesiones, CSRF y flujos principales con la base configurada.

## Relación de una solicitud

Las rutas de los blueprints validan la petición y la sesión; delegan las reglas de negocio y consultas a `app/modelos/`; los modelos usan `app/db.py` y el esquema de `database/schema.sql`; finalmente, Flask presenta los datos en `app/templates/` y los estilos y comportamientos compartidos se cargan desde `app/static/`.
