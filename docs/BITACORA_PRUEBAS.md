# Bitácora de pruebas y reportes — FinovaTech (PMV)

**Actividad:** Instructivo de pruebas y reportes para el PMV (SENA, Guía 7)
**Proyecto:** FinovaTech — Sistema de finanzas personales para estudiantes de bachillerato
**Stack:** Python 3.14.8 · Flask 3.1.3 · PyMySQL 1.2.3 · MySQL (XAMPP)
**Entorno de ejecución:** Windows 11 · pytest 9.2.0 · fpdf2 2.9.0 · matplotlib 3.11.2
**Fecha de la bitácora:** 18/11/2026
**Responsable:** Equipo RDV Systems (aprendiz en formación)

> **Nota sobre el puerto de MySQL.** La guía menciona el puerto 3307; en este
> equipo XAMPP escucha en el **3306**. El proyecto no tiene el puerto
> "quemado": lo lee de `DB_PORT` en `.env`. Para usar 3307 basta con cambiar
> esa variable y reiniciar el servidor. Las pruebas de esta bitácora se
> ejecutaron contra el MySQL real configurado (3306) y la base `finovatech`.

---

## 1. Comandos para reproducir la evidencia

```bat
:: 1) Instalar dependencias (incluye pytest, fpdf2 y matplotlib)
.venv\Scripts\python.exe -m pip install -r requirements.txt

:: 2) Ejecutar la suite única
.venv\Scripts\python.exe -m pytest -v
```

Resultado obtenido el 18/11/2026:

```text
28 passed in 29.16s
  tests/test_finovatech.py .... 28 passed
    · 22 casos del flujo general del sistema (incluye configuración .env)
    ·  6 casos de la actividad (CP-01 a CP-06)
```

Todas las pruebas viven en **un solo archivo**: `tests/test_finovatech.py`.
Los casos CP crean cuentas `actividad_<uuid>@test.local` y las eliminan al
finalizar. El flujo general sí modifica el presupuesto de la cuenta demo, por
lo que tras ejecutar la suite conviene restaurar con
`python -m scripts.seed_demo` antes de una presentación.

### ¿Qué hace la suite única `tests/test_finovatech.py`?

1. Crea la aplicación Flask una sola vez con `create_app()` y la usa con
   `app.test_client()`, de modo que las pruebas hablan con las rutas reales.
2. Prueba el flujo general: páginas públicas y protegidas, CSRF, registro,
   login, bloqueo tras 5 fallos, lista con filtros y paginación, creación y
   borrado de movimientos, presupuesto, perfil, notificaciones, agendamiento,
   supervisión, bitácora, recuperación de contraseña y reportes con CSV.
3. Añade los 6 casos de la actividad (CP-01 a CP-06) con el patrón
   **preparar → ejecutar → verificar** y una fixture `cuenta` que crea y
   elimina una cuenta de estudiante aislada por cada caso.
4. Verifica la integración real con MySQL a través de `app/db.py`, la
   generación del PDF y la detección de intentos de inyección SQL.
5. Los casos CP limpian su cuenta temporal (reportes, ingresos, gastos,
   presupuesto, agendamientos, bitácora, vínculos, estudiante y usuario). El
   flujo general usa la cuenta demo y requiere `scripts.seed_demo` para
   restaurar el presupuesto después de la suite.

---

## 2. Matriz de casos de prueba

| ID | Módulo | Tipo | Entrada | Esperado | Obtenido | ¿Pasa? |
|---|---|---|---|---|---|---|
| CP-01 | `app/modelos/finanzas.py` → `crear_registro` | Unitaria | Gasto con monto `-5`, categoría "Prueba" | Retorna `(False, mensaje)` y no inserta | `False`, "El monto debe ser mayor a cero." | Sí |
| CP-02 | `crear_registro` (validación de límite) | Límite | Monto `0` y luego monto `1` | `0` rechazado; `1` aceptado y guardado | `0` → `False` ("mayor a cero"); `1` → `True` ("Gasto de $1 registrado correctamente.") | Sí |
| CP-03 | `/lista`, `/registro/nuevo`, `/registro/eliminar/Gasto/<id>` | Funcional | Gasto "Gasto CP03 …" por `$4.321` | Se crea, aparece en `/lista`, se elimina y desaparece | HTTP 302 + `?ok=`, texto y `$4.321` visibles, borrado 302 + `?ok=`, descripción ausente al final | Sí |
| CP-04 | `/login` + `verificar_login` | Seguridad | Contraseña `' OR '1'='1` | No autentica; mensaje de credenciales incorrectas | HTTP 200, "Correo o contraseña incorrectos", sesión sin `user_email`, `/panel` redirige a login | Sí |
| CP-05 | `app/db.py` → `get_connection` | Integración | Conexión MySQL y consulta a `information_schema` | Base `finovatech` y tabla `reporte` existente | Base `finovatech`, 1 coincidencia para `reporte` | Sí |
| CP-06 | `app/modelos/reportes.py` → `generar_pdf_resumen` | Reporte | Ingreso `$1.000` + gasto `$250` del mes actual | PDF válido, no vacío, con título y totales | `%PDF-`, más de 900 bytes, contiene "Resumen mensual", `$1.000`, `$250` y saldo `$750` | Sí |

### Resumen de la matriz

| Estado | Cantidad |
|---|---|
| Casos ejecutados | 6 |
| Casos aprobados | 6 |
| Casos fallidos | 0 |
| Defectos abiertos | 0 |

Durante la ejecución **no se presentaron fallos**. Por lo tanto no fue
necesario decidir entre corregir el programa o la prueba. La regla de la
actividad queda documentada: ante un fallo se corrige el **programa**, nunca
la prueba, para que la prueba siga midiendo el comportamiento real.

### Evidencia de los reportes nuevos

| Recurso | Ruta | Verificación |
|---|---|---|
| PDF "Resumen mensual" | `GET /reportes/pdf` | HTTP 200 · `application/pdf` · 9.623 bytes · inicia con `%PDF-` |
| Gráfico de gastos | `GET /reportes/grafico` | HTTP 200 · `image/png` · 43.326 bytes · inicia con firma PNG |
| Botones en la interfaz | `/reportes` | Enlaces `/reportes/pdf` y `/reportes/grafico` presentes junto al CSV |

El PDF incluye: título, fecha y hora de generación, periodo, encabezados con
unidad `($)`, movimientos ordenados por fecha, total de ingresos, total de
gastos y saldo. El gráfico usa matplotlib con backend `Agg` (sin ventana) y
agrupa los gastos por categoría del mes.

---

## 3. Preguntas del punto 2.2 (instructivo de pruebas y reportes)

> Respuestas propuestas para un estudiante de bachillerato, redactadas con
> lenguaje sencillo y ejemplos del proyecto FinovaTech.

### 3.1 ¿Qué es un instructivo de pruebas y para qué sirve en el PMV?

Es un documento que explica **qué se va a probar, cómo se prueba, con qué
datos y qué resultado se espera**. En el PMV (Producto Mínimo Viable) sirve
para demostrar que las funciones indispensables —registro, login, movimientos
y reportes— realmente funcionan antes de mostrarlas al cliente o al jurado.
También permite que otra persona repita las pruebas y obtenga el mismo
resultado.

### 3.2 ¿Qué tipos de pruebas debe incluir un instructivo como este?

Debe incluir, como mínimo:

- **Unitarias:** prueban una sola función (por ejemplo, que `crear_registro`
  rechace un monto negativo).
- **De límite:** revisan los valores extremos (monto `0` rechazado y monto
  `1` aceptado).
- **Funcionales:** recorren un flujo completo (crear un gasto, verlo en la
  lista y eliminarlo).
- **De integración:** comprueban que las piezas se conectan bien (la
  aplicación con MySQL y la tabla `reporte`).
- **De seguridad:** intentan romper el sistema (por ejemplo, una inyección
  SQL en el login).
- **De reportes:** verifican que el PDF y el gráfico se generen con datos
  correctos.

### 3.3 ¿Qué debe contener un reporte de pruebas?

Como mínimo:

1. Identificación del caso (ID, módulo y tipo de prueba).
2. Datos de entrada utilizados.
3. Resultado esperado.
4. Resultado obtenido.
5. Conclusión: ¿pasa o no pasa?
6. Fecha, entorno (sistema operativo, versiones) y responsable.
7. Evidencia (captura, archivo generado o salida de la consola).

En esta bitácora todo eso está en la matriz de casos y en la sección de
evidencia de los reportes.

### 3.4 ¿Cómo se relacionan las pruebas con los reportes y con la toma de decisiones?

Las pruebas producen **datos confiables**; los reportes los presentan de forma
clara (tabla de casos, PDF y gráfico). Con esa información el equipo decide si
el PMV está listo para presentarse, qué defectos corregir primero y qué
mejoras quedan para la siguiente versión. Sin pruebas, un reporte bonito
podría estar mostrando información equivocada.

---

## 4. Comprueba lo que aprendiste (8 preguntas)

### 4.1 ¿Qué es el PMV y por qué se prueba antes de venderlo?

El PMV (Producto Mínimo Viable) es la versión más pequeña del sistema que ya
entrega valor real: en FinovaTech, registrarse, iniciar sesión, anotar
ingresos/gastos y descargar un reporte. Se prueba antes de venderlo para no
invertir tiempo ni dinero en funciones que todavía fallan y para proteger la
reputación del equipo.

### 4.2 ¿Cuál es la diferencia entre prueba unitaria, funcional y de integración?

- **Unitaria:** revisa una función aislada, por ejemplo `crear_registro` con
  un monto negativo.
- **Funcional:** revisa una tarea completa del usuario, por ejemplo crear un
  gasto y verlo en `/lista`.
- **Integración:** revisa la unión entre partes, por ejemplo la aplicación
  Flask conectándose a MySQL y encontrando la tabla `reporte`.

### 4.3 ¿Qué es un caso límite? Da un ejemplo del proyecto.

Es una prueba con el valor más pequeño o más grande permitido, o justo en el
borde. Ejemplo: el monto de un movimiento debe ser mayor que cero; por eso
se prueba `0` (debe fallar) y `1` (debe pasar). Así se descubre si la
validación se aplica exactamente donde debe.

### 4.4 ¿Qué es una prueba de seguridad y qué se buscó en CP-04?

Es una prueba que intenta usar el sistema de forma maliciosa para comprobar
que está protegido. En CP-04 se escribió `' OR '1'='1` como contraseña para
intentar engañar a la consulta SQL. El resultado fue correcto: el sistema no
autenticó al usuario porque usa consultas parametrizadas y compara hashes de
contraseña.

### 4.5 ¿Qué es un reporte y qué datos debe mostrar?

Un reporte es un resumen ordenado de la información del sistema. El "Resumen
mensual" de FinovaTech muestra título, fecha y hora de generación, periodo,
movimientos ordenados por fecha, monto con unidad `($)`, total de ingresos,
total de gastos y saldo. Su objetivo es que el estudiante entienda su situación
financiera sin revisar la base de datos.

### 4.6 ¿Por qué es importante documentar los resultados de las pruebas?

Porque deja **evidencia** de que el sistema funciona y permite repetir la
verificación en el futuro. Si algo se daña después, la bitácora ayuda a
encontrar qué cambió. También facilita el trabajo en equipo: otra persona
puede ejecutar los mismos comandos y comprobar los mismos resultados.

### 4.7 ¿Qué es un defecto y cómo se reporta?

Un defecto (o bug) es una diferencia entre lo que el sistema **debería** hacer
y lo que **hace**. Se reporta con: título corto, módulo afectado, pasos para
reproducirlo, resultado esperado, resultado obtenido, evidencia y prioridad.
En esta actividad, la matriz de casos sería el lugar donde se anotaría el
defecto si alguna fila dijera "No" en la columna "¿Pasa?".

### 4.8 ¿Cómo se decide que el PMV está listo para presentarse?

Cuando todas las pruebas críticas (unitarias, de límite, funcionales, de
integración, de seguridad y de reportes) están aprobadas, no quedan defectos
de prioridad alta y los reportes muestran datos correctos. En este caso la
evidencia es: `28 passed`, matriz con 6 de 6 casos aprobados, PDF válido y
gráfico PNG generado.

---

## 5. Cambios realizados en esta actividad

| Archivo | Cambio |
|---|---|
| `requirements.txt` | Se agregaron `pytest`, `fpdf2` y `matplotlib`. |
| `app/modelos/reportes.py` | Nuevo módulo: resumen mensual, PDF y gráfico PNG (matplotlib `Agg`). |
| `app/blueprints/registros.py` | Rutas `GET /reportes/pdf` y `GET /reportes/grafico` con sesión obligatoria. |
| `app/templates/reportes.html` | Botones "Resumen mensual (PDF)" y "Gráfico (PNG)" junto al CSV. |
| `tests/test_finovatech.py` | Suite única con los 28 casos: 22 del flujo general + CP-01 a CP-06 con fixtures y limpieza de datos. |

No se modificó la lógica existente: se reutilizan `crear_registro`,
`get_estudiante_id`, `_fmt` y `get_connection`.
