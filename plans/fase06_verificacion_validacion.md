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

Fecha de verificación: 2026-11-03. Entorno: Python 3.14.8, MariaDB 10.4.32
(XAMPP) en el puerto 3307, servidor Flask en 5001.

- Suite `python -m tests.test_smoke`: **23 comprobaciones OK**, sin fallos.
  Cubre rutas públicas y aliases, redirección de rutas protegidas, registro de
  usuario, login demo con `/panel` 200, `/lista` autenticada, rechazo de POST
  sin CSRF, presupuesto del panel y su edición desde `/presupuesto`,
  notificaciones autenticadas, validación de
  fecha/hora/categoría del agendamiento, agendamiento con y sin sesión, y
  logout solo por POST.
- Salida final: `Todos los smoke tests v10 pasaron.`
- `GET /` con el servidor activo: HTTP 200.
- Cuenta demo validada contra el hash almacenado:
  `adminr123@gmail.com` / `123456789` (rol administrador).
- Prueba manual en Opera de los flujos principales (registro, login, panel,
  lista, notificaciones y agendamiento): confirmada por el usuario.

## Iteración v10.3.4 — RF-13 Perfil de usuario

Verificación ejecutada el 2026-11-06:

- `/perfil` sin sesión redirige a `/login` (302) y con sesión responde 200.
- El perfil muestra nombre, usuario, correo, rol y fecha de registro.
- Actualización de nombre/usuario persistida y reflejada en la sesión.
- Nombre de usuario duplicado rechazado con mensaje de error.
- Contraseña actual incorrecta rechazada; cambio correcto confirmado.
- Login exitoso con la nueva contraseña.
- Suite completa: **25 comprobaciones OK**, sin fallos.
- Salida final: `Todos los smoke tests v10 pasaron.`
- Verificación contra el servidor real en `http://localhost:5001`: login demo
  y `/perfil` 200 con ambos formularios.

Estado: fase 06 cerrada para v10.3.4; RF-13 verificado.

## Iteración RNF-10 — Pruebas de escritura y anti fuerza bruta

### Objetivo

Cubrir con pruebas reales (sin mocks) la creación/eliminación de movimientos y
el bloqueo del login después de cinco intentos fallidos.

### Alcance

- Registrar un usuario de prueba, crear un gasto real desde `/registro/nuevo`,
  comprobar que aparece en `/lista` y eliminarlo desde su formulario.
- Verificar que el bloqueo aparece tras cinco fallos y que persiste incluso con
  la contraseña correcta en el siguiente intento.
- No incluye pruebas de carga ni automatización de navegador.

### Criterios de aceptación

- El movimiento creado existe en la base y desaparece tras eliminarlo.
- El sexto intento de login muestra el mensaje de bloqueo.
- La suite completa queda en verde y sin mocks en estos dos flujos.

### Evidencia

- Verificación ejecutada el 2026-11-06 con `python -m tests.test_smoke`.
- Alta real: `POST /registro/nuevo` confirmó `ok`, el gasto apareció en
  `/lista` con su monto y se localizó su formulario de eliminación.
- Baja real: `POST /registro/eliminar/Gasto/<id>` confirmó `ok` y el gasto
  dejó de aparecer en `/lista`.
- Anti fuerza bruta: cinco fallos con una cuenta aislada activaron el bloqueo;
  el sexto intento, con la contraseña correcta, mostró
  `Demasiados intentos fallidos` y el tiempo de espera.
- Suite completa: **27 comprobaciones OK**, sin fallos.
- Salida final: `Todos los smoke tests v10 pasaron.`

Estado: fase 06 cerrada para v10.3.5; RNF-10 verificado.
## Iteración v10.3.6 - RF-15 a RF-18

### Objetivo

Verificar los flujos nuevos de filtros/paginación, supervisión, bitácora y
recuperación de contraseña con pruebas de integración reales.

### Criterios de aceptación

- `/lista` devuelve solo los resultados filtrados y respeta páginas de 10.
- Un padre vinculado por código ve únicamente a sus estudiantes.
- La bitácora registra login correcto, fallido y bloqueo.
- Un token de recuperación se usa una vez y permite iniciar sesión.

### Evidencia

- Ejecución de `python -m tests.test_smoke` el 2026-11-06: **34 comprobaciones
  OK**, sin fallos, con salida `Todos los smoke tests v10 pasaron.`
- RF-15: `test_lista_filtros_y_paginacion` confirmó que `q` y `tipo` limitan
  resultados en MySQL y que la lista pagina de 10 en 10 (`Página 1 de 2`,
  `Página 2 de 2`).
- RF-16: `test_supervision_padre_vincula_y_desvincula` confirmó el código en
  `/perfil`, la vinculación, la visibilidad del estudiante y la desvinculación;
  un estudiante recibe 302 al intentar entrar a `/supervision`.
- RF-17: `test_bitacora_accesos_admin` confirmó el evento de login correcto y
  el 302 de un estudiante hacia `/panel`.
- RF-18: `test_recuperacion_password_token_un_uso` confirmó el mensaje genérico,
  el cambio de contraseña, el login con la nueva clave y el rechazo de
  reutilización del token.
- Verificación de datos demo: 15 ingresos, 40 gastos, 12 categorías, presupuesto
  `$600.000` con `$700.000` gastados (117 %), 6 notificaciones y cuenta de padre
  `padredemo@gmail.com` con acceso a `/supervision`.
- La portada mostró estadísticas reales de la base (usuarios, movimientos y
  categorías) mediante `_contar_usuarios`, `_contar_movimientos` y
  `_contar_categorias`.

Estado: **cerrada** (2026-11-06) para v10.3.6; RF-15 a RF-18 verificados.
