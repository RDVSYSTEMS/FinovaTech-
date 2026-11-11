# REQUISITOS DEL PROYECTO — FinovaTech v10.3

**Proyecto:** Sistema de Finanzas Personales para Estudiantes de Bachillerato
**Empresa desarrolladora:** RDV Systems
**Entidad formadora:** SENA
**Versión del documento:** 10.3.6
**Estado:** Documentación consolidada de la versión v10.3 (contexto educativo)

---

## 1. Información general

| Dato | Valor |
|---|---|
| Nombre del sistema | FinovaTech |
| Tipo | Aplicación web |
| Frontend | HTML5, CSS3, JavaScript (vanilla) |
| Backend | Python 3.14 + Flask |
| Base de datos | MySQL 5.x / MariaDB 10.4 (XAMPP, puerto configurable con `DB_PORT`) |
| Control de versiones | Git + GitHub (RDVSYSTEMS/FinovaTech-) |
| Usuarios destino | Estudiantes de bachillerato |

---

## 2. Propósito y alcance

El sistema permite a estudiantes de bachillerato llevar el control de sus
finanzas personales (ingresos, gastos, presupuesto y reportes) desde una
aplicación web educativa. El alcance cubre:

- Registro y autenticación de usuarios.
- Registro, consulta y eliminación de ingresos y gastos.
- Panel de resumen con totales, gráficas y evolución mensual.
- Presupuesto mensual con alertas.
- Notificaciones automáticas sobre el comportamiento financiero.
- Agendamiento de sesiones de educación financiera.
- Generación de reportes (procedimiento almacenado).
- Vista de resumen financiero por usuario (vista SQL).

Queda **fuera de alcance**: integración con pasarelas de pago reales, banca
en línea, y despliegue en servidores de producción externos.

---

## 3. Usuarios y roles

| Rol | Descripción |
|---|---|
| Estudiante | Usuario principal: gestiona sus ingresos/gastos/presupuesto |
| Padre | Perfil de registro permitido (supervisión básica) |
| Administrador | Creado solo desde la base de datos; gestiona el sistema |

> Regla de seguridad: el **auto-registro público solo permite los roles**
> estudiante y padre (lista blanca del lado del servidor). El rol administrador
> corresponde a los programadores del sistema y no se puede crear desde el
> formulario público.

---

## 4. Requisitos funcionales

### RF-01 Registro de usuario
- El sistema permite crear una cuenta con: nombres, correo, usuario,
  contraseña, confirmación de contraseña y tipo de cuenta.
- Valida el lado del servidor: campos completos, rol permitido,
  contraseña ≥ 8 caracteres, contraseñas coincidentes.
- Cifra la contraseña (werkzeug `generate_password_hash`) y nunca la
  guarda en texto plano.
- Rechaza correos/usuarios duplicados.
- Crea automáticamente el perfil de estudiante solo cuando el rol es
  `estudiante`; el rol `padre` no crea perfil financiero propio.

### RF-02 Inicio de sesión
- Verifica correo + contraseña contra la base de datos.
- Rota la sesión al iniciar (previene fijación de sesión).
- Bloquea la combinación IP+correo tras 5 intentos fallidos (bloqueo que
  se duplica: 2 → 4 → 8 minutos).

### RF-02.1 Validación en vivo de los formularios
- Login y registro validan en el cliente (JavaScript) al salir de cada campo
  y al enviar: marcan el campo en rojo/verde y muestran un mensaje por campo.
- Si hay campos inválidos, el envío se bloquea y el formulario vibra (`shake`).
- La validación del servidor se mantiene como fuente de verdad (campos
  obligatorios, formato, longitud, coincidencia, rol permitido y duplicados).

### RF-03 Cierre de sesión
- Elimina la sesión y redirige a la página principal.

### RF-04 Panel principal
- Muestra: total de ingresos, total de gastos, balance, cantidad de
  registros y últimos 6 movimientos.
- Gráfica de gastos por categoría y curva de evolución (6 meses).
- Barra de presupuesto del mes vigente (límite, gastado, disponible).
- La interfaz incluye barra de progreso de lectura, entrada escalonada del
  sidebar y las tarjetas, y se adapta sin desbordamiento horizontal entre
  1025 y 1120px (las estadísticas pasan a dos columnas antes de recortar el monto).

### RF-05 Gestión de movimientos (ingresos y gastos)
- Permite registrar un movimiento con tipo, descripción, monto,
  categoría y fecha.
- Ordena el historial del más reciente al más antiguo.
- Permite eliminar un movimiento **solo si pertenece al usuario**.
- Mantiene al día `saldo_actual` del estudiante mediante triggers.

### RF-06 Presupuesto
- Permite definir un monto límite por periodo (mensual) desde `/presupuesto`.
- El formulario crea el presupuesto del mes vigente o actualiza el existente,
  con validación de monto positivo y máximo permitido.
- Advierte al alcanzar el 80% y al superar el 100%.

### RF-07 Notificaciones
- Generadas desde datos reales:
  - Registro reciente por movimiento.
  - Presupuesto cerca/superado.
  - Gasto elevado (>40% del mes).
  - Buen manejo o saldo negativo del mes.

### RF-08 Reportes (backend)
- Procedimiento `sp_generar_reporte` guarda un reporte con totales.
- Procedimiento `sp_resumen_mensual` devuelve el resumen de un mes.

### RF-09 Páginas institucionales
- Inicio, contacto, servicios, soporte y términos accesibles sin sesión.
- Inicio y servicios usan el video institucional como fondo y presentan una
  llamada a la acción final; cada tarjeta de servicio dirige a `/login`.
- La portada muestra estadísticas reales (usuarios y movimientos) leídas de la
  base de datos, no valores simulados.

### RF-10 Agendamiento de sesiones
- Permite reservar una sesión indicando fecha, hora, categoría, estado y comentarios.
- Rechaza fechas anteriores al día actual y valores no permitidos.
- Guarda cada agendamiento asociado al usuario autenticado.

### RF-12 Reportes en la app
- `/reportes` muestra los totales del estudiante y el historial de los últimos
  20 reportes generados.
- El formulario genera un reporte mediante el stored procedure
  `sp_generar_reporte` (tabla `reporte`) y confirma con un mensaje en pantalla.
- El menú del panel incluye la sección Reportes para los roles autenticados.

### RF-13 Perfil de usuario
- Permite consultar los datos de la cuenta: nombre, usuario, correo, rol y fecha
  de registro.
- Permite actualizar el nombre y el nombre de usuario; el correo y el rol no se
  editan desde este formulario.
- Rechaza un nombre de usuario duplicado o con longitud menor a 4 caracteres.
- Permite cambiar la contraseña verificando primero la contraseña actual,
  exigiendo mínimo 8 caracteres y confirmación coincidente.
- Actualiza el nombre mostrado en la sesión después de guardar los datos.

### RF-14 Exportación de movimientos (CSV)
- `/exportar` descarga todos los movimientos del estudiante autenticado como
  CSV (tipo, descripción, monto, fecha y categoría).
- El archivo viaja con BOM UTF-8 para que Excel muestre tildes y eñes
  correctamente.
- Exige sesión iniciada; cada usuario solo descarga sus propios movimientos.

### RF-15 Paginación y filtros en servidor
- `/lista` acepta `q` (texto de descripción) y `tipo` (`Ingreso` o `Gasto`)
  como filtros enviados por GET y resueltos en MySQL, no en el navegador.
- Muestra 10 movimientos por página, conserva los filtros al navegar y
  presenta el total de resultados filtrados.
- Rechaza valores de `tipo` fuera de la lista blanca y limita el texto de
  búsqueda para evitar consultas costosas.

### RF-16 Supervisión para el rol padre
- El estudiante ve en `/perfil` un código de vinculación único y no editable.
- El padre ingresa ese código en `/supervision` para vincular una cuenta de
  estudiante; no puede vincular por correo ni ver estudiantes sin código.
- La vista de supervisión muestra, por estudiante vinculado, sus totales,
  presupuesto y últimos movimientos en modo solo lectura.
- El padre puede desvincular a un estudiante; la operación solo afecta sus
  propios vínculos.

### RF-17 Bitácora de accesos
- Registra inicios de sesión correctos, intentos fallidos, bloqueos y cierres
  de sesión con correo, IP, evento, detalle y fecha.
- El rol administrador consulta los últimos 100 eventos en `/bitacora`.
- La bitácora es solo de lectura y no permite modificar ni borrar registros
  desde la aplicación.

### RF-18 Recuperación de contraseña
- `/recuperar` recibe un correo y responde siempre con el mismo mensaje para
  no revelar si la cuenta existe.
- Si la cuenta existe, genera un token de un solo uso, válido por 30 minutos,
  y envía el enlace por SMTP configurado en variables de entorno.
- Sin SMTP configurado, el enlace se escribe en el log del servidor para
  permitir la prueba local, sin mostrarlo en la respuesta HTTP.
- `/restablecer/<token>` valida el token, exige contraseña de mínimo 8
  caracteres y confirmación coincidente, actualiza el hash y marca el token
  como usado.

---

## 5. Requisitos no funcionales

| Código | Requisito | Implementación |
|---|---|---|
| RNF-01 | Contraseñas nunca en texto plano | `werkzeug.security` |
| RNF-02 | Protección CSRF en todo POST | token por sesión + `hmac.compare_digest` |
| RNF-03 | Cookies de sesión seguras | HttpOnly + SameSite=Lax |
| RNF-04 | Cabeceras de seguridad HTTP | X-Frame-Options, CSP, nosniff, Referrer-Policy, Permissions-Policy |
| RNF-05 | Anti fuerza bruta | bloqueo progresivo por IP+correo |
| RNF-06 | Contra inyección SQL | parámetros `%s` + nombres de tabla en lista blanca |
| RNF-07 | Sesiones y datos en español | interfaz 100% en español (formato moneda COP) |
| RNF-08 | Portabilidad local | corre en Windows con XAMPP sin configuración extra |
| RNF-09 | Animaciones accesibles | animaciones CSS/AOS respetan `prefers-reduced-motion` |
| RNF-10 | Pruebas de escritura y anti fuerza bruta | `tests/test_smoke.py` cubre crear/eliminar movimientos reales y el bloqueo tras 5 intentos, sin mocks |

---

## 6. Requisitos de base de datos

- Motor InnoDB en tablas de negocio; utf8mb4 / utf8mb4_general_ci.
- Once tablas: `administrador`, `usuario`, `estudiante`, `ingreso`,
  `gasto`, `presupuesto`, `reporte`, `agendamiento`, `padre_estudiante`,
  `bitacora_acceso`, `recuperacion_password`.
- `estudiante.codigo_vinculacion` es único y se genera bajo demanda para
  autorizar la supervisión del padre.
- Cuatro triggers que mantienen `estudiante.saldo_actual`.
- Cuatro stored procedures: `sp_registrar_movimiento`,
  `sp_eliminar_movimiento`, `sp_resumen_mensual`, `sp_generar_reporte`.
- Una vista: `vista_resumen_financiero`.
- Detalle completo en `docs/MODELO_DATOS.md`.

---

## 7. Criterios de aceptación

1. Un usuario nuevo se registra, cierra sesión y vuelve a entrar.
2. El panel muestra datos reales de la base de datos (no simulados).
3. Un ingreso/gasto creado aparece al instante en la lista y en el saldo.
4. No se puede eliminar un movimiento de otro usuario.
5. Un POST sin token CSRF es rechazado con 400.
6. Tras 5 intentos fallidos de login, la cuenta se bloquea temporalmente.
7. Con MySQL apagado, la aplicación avisa (no crashea) en el arranque.
8. El usuario `root` de XAMPP (sin contraseña) conecta sin cambios.
9. Una sesión válida de agendamiento se guarda asociada al usuario autenticado.
10. Una fecha anterior al día actual o un valor no permitido se rechaza.
11. El usuario puede cambiar su nombre y nombre de usuario, y el cambio persiste.
12. Un nombre de usuario duplicado se rechaza.
13. El cambio de contraseña exige la contraseña actual y permite entrar con la nueva.
14. Una contraseña actual incorrecta o una nueva demasiado corta se rechaza.
15. `/lista` filtra por texto y tipo en MySQL, pagina de 10 en 10 y mantiene
    los filtros entre páginas.
16. Un padre solo ve estudiantes vinculados con un código válido y no puede
    modificar sus datos.
17. El administrador consulta en `/bitacora` los eventos de acceso recientes.
18. Un enlace de recuperación válido permite cambiar la contraseña una sola
    vez y luego inicia sesión con la nueva.

---

## 8. Verificación

- `tests/test_smoke.py` cubre 34 comprobaciones: públicas 200, protegidas →
  login, aliases `.html`, registro de usuario, login demo + panel, acceso a
  lista, rechazo de POST sin token CSRF, presupuesto coherente y editable,
  notificaciones, validación del agendamiento (fecha, hora, categoría y
  sesión), perfil (datos y contraseña), creación/eliminación real de un
  movimiento, bloqueo del login tras 5 intentos, logout solo por POST, filtros
  y paginación, supervisión padre–estudiante, bitácora y recuperación de
  contraseña con token de un solo uso.
- La suite smoke requiere MySQL/MariaDB encendido, el esquema aplicado y la
  cuenta demo disponible; no sustituye pruebas unitarias o de navegador.
- Script `scripts/seed_demo.py` genera datos de demostración repetibles.

---

## 9. Mapa de rutas

### Rutas públicas

| Método | Ruta | Responsabilidad |
|---|---|---|
| GET | `/` | Página principal. |
| GET/POST | `/login` | Inicio de sesión y validación de credenciales. |
| GET/POST | `/registro` | Creación de cuentas y perfil de estudiante. |
| POST | `/logout` | Cierre de sesión protegido por CSRF. |
| GET/POST | `/recuperar` | Solicitud de enlace de recuperación. |
| GET/POST | `/restablecer/<token>` | Cambio de contraseña con token de un uso. |
| GET | `/<pagina>.html` | Aliases de páginas públicas permitidas. |

### Rutas protegidas

| Método | Ruta | Responsabilidad |
|---|---|---|
| GET | `/panel` | Resumen financiero y gráficas. |
| GET | `/lista` | Historial de ingresos y gastos. |
| GET/POST | `/presupuesto` | Consulta, creación y actualización del presupuesto mensual. |
| POST | `/registro/nuevo` | Creación de un ingreso o gasto. |
| POST | `/registro/eliminar/<tipo>/<id>` | Eliminación autorizada de un movimiento. |
| GET | `/notificacion` | Notificaciones calculadas del usuario. |
| GET | `/agendamiento` | Formulario para reservar una sesión. |
| POST | `/agendamiento` | Validación y guardado de una sesión. Devuelve JSON. |
| GET | `/perfil` | Datos de la cuenta y formularios de edición. |
| POST | `/perfil` | Actualización de nombre y nombre de usuario. |
| POST | `/perfil/password` | Cambio de contraseña con verificación de la actual. |
| GET | `/supervision` | Supervisión de estudiantes vinculados (rol padre). |
| POST | `/supervision/vincular` | Vinculación mediante código del estudiante. |
| POST | `/supervision/desvincular/<id>` | Baja de un vínculo del padre actual. |
| GET | `/bitacora` | Últimos 100 eventos de acceso (rol administrador). |

Todas las rutas `POST` requieren `csrf_token`. Las rutas protegidas requieren
una sesión activa y limitan las operaciones a los datos del usuario actual.

## 10. Contrato de agendamiento

El formulario envía estos campos mediante `POST /agendamiento`:

| Campo | Obligatorio | Valores o formato |
|---|---|---|
| `fecha` | Sí | `YYYY-MM-DD`, desde el día actual. |
| `hora` | Sí | `HH:MM`. |
| `categoria` | Sí | `reserva`, `consultoria` o `taller`. |
| `estado` | No | `pendiente`, `confirmado`, `cancelado` o `completado`. |
| `comentarios` | No | Texto de hasta 1000 caracteres. |
| `csrf_token` | Sí | Token de seguridad de la sesión. |

Una respuesta exitosa devuelve `{ "ok": true, "mensaje": "..." }`. Los
errores de validación devuelven HTTP 400 con `ok: false` y un mensaje.
