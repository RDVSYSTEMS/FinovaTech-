# FinovaTech v9

Sistema de Finanzas Personales para Estudiantes de Bachillerato.
Aplicación web (HTML/CSS/JS + Flask + MySQL) con autenticación, control de
ingresos/gastos, presupuesto y notificaciones. Proyecto de grado SENA —
desarrollado por **RDV Systems**.

> Nota de versionado: este repositorio comienza en **v1.0.0** en Git/GitHub
> (es el primer commit), aunque la carpeta del proyecto se llame "FinovaTech v9".

## Requisitos previos

- Python 3.13
- XAMPP con Apache + MySQL/MariaDB (usuario `root`, sin contraseña)
- Git

## Instalación

```powershell
# 1. Entorno virtual
py -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 2. Configuración
copy .env.example .env     # completa SECRET_KEY (o genera una: python -c "import secrets; print(secrets.token_hex(32))")

# 3. Base de datos (con MySQL de XAMPP encendido, puerto 3306)
$sql = Get-Content -Raw -LiteralPath "database\schema.sql"
$sql | C:\xampp\mysql\bin\mysql.exe -u root --default-character-set=utf8mb4

# 4. Datos de demostración
.venv\Scripts\python -m scripts.seed_demo
```

## Ejecutar

Doble clic en `iniciar.bat` (valida MySQL en 3306 y abre el navegador) o:

```powershell
.venv\Scripts\python run.py
```

Servidor en http://localhost:5000

### Cuenta de demostración
- Correo: `adminr123@gmail.com`
- Contraseña: `123456789`

## Estructura del proyecto

```
FinovaTech v9/
├── run.py                  # Punto de entrada (create_app + run)
├── iniciar.bat             # Lanzador (verifica MySQL 3306)
├── requirements.txt
├── .env / .env.example     # Configuración (NO subir .env a Git)
├── app/                    # Paquete de la aplicación
│   ├── __init__.py         # Fábrica create_app (factory pattern)
│   ├── config.py           # Config (variables de entorno)
│   ├── db.py               # Conexión MySQL (PyMySQL)
│   ├── seguridad.py        # CSRF, cabeceras, login_requerido, anti fuerza bruta
│   ├── blueprints/         # publicas, panel, registros, notificaciones
│   ├── modelos/            # usuarios.py, finanzas.py (acceso a datos)
│   ├── templates/          # Plantillas HTML
│   └── static/             # CSS, JS, imágenes, vendor
├── database/
│   └── schema.sql          # 7 tablas + triggers + procedures + vista
├── scripts/
│   └── seed_demo.py        # Datos de demostración repetibles
├── tests/
│   └── test_smoke.py       # Smoke tests (públicas, login, CSRF)
└── docs/
    ├── REQUISITOS.md       # Documento SRS (RF, RNF, criterios)
    └── MODELO_DATOS.md     # ER, tablas, triggers, procedures, vista
```

## Seguridad

- Contraseñas cifradas (`werkzeug.security`).
- Token CSRF por sesión validado con `hmac.compare_digest`.
- Cookies HttpOnly + SameSite=Lax; rotación de sesión en login.
- Cabeceras HTTP (CSP, X-Frame-Options, nosniff, Referrer-Policy,
  Permissions-Policy).
- Bloqueo anti fuerza bruta (5 fallos → 2 min, duplicado progresivo).
- SQL con parámetros `%s` y nombres de tabla en lista blanca.

## Pruebas

```powershell
.venv\Scripts\python -m tests.test_smoke
```

## Historial de versiones

| Versión (Git) | Contenido |
|---|---|
| v1.0.0 | Primera versión liberada del repositorio (estructura por capas v9) |