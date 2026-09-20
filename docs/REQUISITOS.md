# REQUISITOS DEL PROYECTO — FinovaTech v9

**Proyecto:** Sistema de Finanzas Personales para Estudiantes de Bachillerato
**Empresa desarrolladora:** RDV Systems
**Entidad formadora:** SENA
**Versión del documento:** 1.0.0
**Estado:** Validado con cliente simulado (contexto educativo)

---

## 1. Información general

| Dato | Valor |
|---|---|
| Nombre del sistema | FinovaTech |
| Tipo | Aplicación web |
| Frontend | HTML5, CSS3, JavaScript (vanilla) |
| Backend | Python 3.13 + Flask |
| Base de datos | MySQL 5.x / MariaDB 10.4 (XAMPP) |
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
- Generación de reportes (procedimiento almacenado).
- Vista de resumen financiero por usuario (vista SQL).

Queda **fuera de alcance**: integración con pasarelas de pago reales, banca
en línea, y despliegue en servidores de producción externos.

---

## 3. Usuarios y roles

| Rol | Descripción |
|---|---|
| Estudiante | Usuario principal: gestiona sus ingresos/gastos/presupuesto |
| Empleado | Perfil de registro permitido (misma funcionalidad básica) |
| Padre | Perfil de registro permitido (supervisión básica) |
| Administrador | Creado solo desde la base de datos; gestiona el sistema |

> Regla de seguridad: el **auto-registro público solo permite los roles**
> estudiante, empleado y padre (lista blanca del lado del servidor).

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
- Crea automáticamente el perfil de estudiante asociado.

### RF-02 Inicio de sesión
- Verifica correo + contraseña contra la base de datos.
- Rota la sesión al iniciar (previene fijación de sesión).
- Bloquea la combinación IP+correo tras 5 intentos fallidos (bloqueo que
  se duplica: 2 → 4 → 8 minutos).

### RF-03 Cierre de sesión
- Elimina la sesión y redirige a la página principal.

### RF-04 Panel principal
- Muestra: total de ingresos, total de gastos, balance, cantidad de
  registros y últimos 6 movimientos.
- Gráfica de gastos por categoría y curva de evolución (6 meses).
- Barra de presupuesto del mes vigente (límite, gastado, disponible).

### RF-05 Gestión de movimientos (ingresos y gastos)
- Permite registrar un movimiento con tipo, descripción, monto,
  categoría y fecha.
- Ordena el historial del más reciente al más antiguo.
- Permite eliminar un movimiento **solo si pertenece al usuario**.
- Mantiene al día `saldo_actual` del estudiante mediante triggers.

### RF-06 Presupuesto
- Permite definir un monto límite por periodo (mensual).
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

---

## 6. Requisitos de base de datos

- Motor InnoDB en tablas de negocio; utf8mb4 / utf8mb4_general_ci.
- Siete tablas: `administrador`, `usuario`, `estudiante`, `ingreso`,
  `gasto`, `presupuesto`, `reporte`.
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

---

## 8. Verificación

- `tests/test_smoke.py` cubre: públicas 200, protegidas → login,
  registro de usuario, login demo + panel, CSRF bloquea POST.
- Script `scripts/seed_demo.py` genera datos de demostración repetibles.