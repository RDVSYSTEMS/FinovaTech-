"""Pruebas smoke del flujo principal de FinovaTech v10.

Comprueba que la aplicación pueda arrancar, que las rutas públicas respondan,
que las rutas privadas exijan autenticación y que los formularios respeten
la protección CSRF. Estas pruebas usan la base de datos configurada y la
cuenta demo, por lo que sirven como verificación rápida de integración local.
"""
import os
import sys
import uuid
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()
app.config["TESTING"] = True


def obtener_csrf(client, url="/login"):
    """Obtiene una página para inicializar la sesión y su token CSRF."""
    r = client.get(url)
    assert r.status_code == 200, f"GET {url} -> {r.status_code}"
    return r, None


def login_demo(client):
    """Inicia sesión con la cuenta demo y deja el cliente autenticado."""
    import re
    r = client.get("/login")
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    r = client.post("/login", data={
        "email": "adminr123@gmail.com",
        "password": "123456789",
        "csrf_token": token,
    }, follow_redirects=False)
    assert r.status_code == 302, f"login demo -> {r.status_code}"
    return client


def crear_cuenta_prueba(client, rol="estudiante", nombre="RNF10 Test"):
    """Registra una cuenta aislada para pruebas de escritura y bloqueo."""
    import re
    unique = uuid.uuid4().hex[:8]
    email = f"rnf10_{unique}@test.local"
    username = f"rnf10_{unique}"
    password = "12345678x"

    r = client.get("/registro")
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    r = client.post("/registro", data={
        "full_name": nombre,
        "email": email,
        "username": username,
        "password": password,
        "confirm_password": password,
        "user_type": rol,
        "csrf_token": token,
    }, follow_redirects=True)
    assert "Cuenta creada correctamente" in r.get_data(as_text=True)
    return email, password


def login_usuario(client, email, password):
    """Inicia sesión con una cuenta de prueba y deja el cliente autenticado."""
    import re
    r = client.get("/login")
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    r = client.post("/login", data={
        "email": email,
        "password": password,
        "csrf_token": token,
    }, follow_redirects=False)
    assert r.status_code == 302, f"login de prueba -> {r.status_code}"
    return client


def test_publicas():
    """Las páginas públicas deben responder sin sesión con HTTP 200."""
    client = app.test_client()
    for url in ("/", "/login", "/registro", "/recuperar", "/contacto.html", "/servicios.html"):
        r = client.get(url)
        assert r.status_code == 200, f"GET {url} -> {r.status_code}"
        print(f"OK  pública  {url}")


def test_protegidas_sin_sesion():
    """Las rutas privadas deben redirigir al login cuando no hay sesión."""
    client = app.test_client()
    for url in ("/panel", "/lista", "/reportes", "/exportar", "/presupuesto", "/notificacion", "/agendamiento", "/perfil", "/supervision", "/bitacora"):
        r = client.get(url)
        assert r.status_code == 302, f"GET {url} sin sesión -> {r.status_code}"
        assert "/login" in r.headers["Location"], f"{url} no redirige a login"
        print(f"OK  protegida {url} -> redirige a login")


def test_aliases_login_registro_html():
    """Los aliases .html de login y registro siguen disponibles."""
    client = app.test_client()
    for url in ("/login.html", "/registro.html"):
        r = client.get(url)
        assert r.status_code == 200, f"GET {url} -> {r.status_code}"
        print(f"OK  alias público {url}")


def test_registro():
    """Registra un usuario nuevo usando un correo y usuario irrepetibles."""
    client = app.test_client()
    r, _ = obtener_csrf(client, "/registro")
    import re
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    # El sufijo evita colisiones al ejecutar la prueba varias veces.
    unique = uuid.uuid4().hex[:8]
    email = f"smoke_{unique}@test.local"
    username = f"smoketest_{unique}"
    r = client.post("/registro", data={
        "full_name": "Smoke Test",
        "email": email,
        "username": username,
        "password": "12345678x",
        "confirm_password": "12345678x",
        "user_type": "estudiante",
        "csrf_token": token,
    }, follow_redirects=True)
    assert r.status_code == 200
    assert "Cuenta creada correctamente" in r.get_data(as_text=True), "No creó la cuenta"
    print("OK  registro nuevo usuario")


def test_login_panel():
    """La cuenta demo puede iniciar sesión y acceder al panel."""
    client = app.test_client()
    r, _ = obtener_csrf(client, "/login")
    import re
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    r = client.post("/login", data={
        "email": "adminr123@gmail.com",
        "password": "123456789",
        "csrf_token": token,
    }, follow_redirects=False)
    assert r.status_code == 302, f"login -> {r.status_code}"
    assert "/panel" in r.headers["Location"], f"login no redirige a /panel: {r.headers.get('Location')}"

    r = client.get("/panel")
    assert r.status_code == 200, f"/panel logueado -> {r.status_code}"
    texto = r.get_data(as_text=True)
    assert "FinovaTech" in texto or "Panel" in texto or "panel" in texto, "Panel sin contenido esperado"
    print("OK  login demo + /panel 200")


def test_lista_y_csrf():
    """La lista exige sesión y el servidor rechaza POST sin CSRF."""
    client = app.test_client()
    r, _ = obtener_csrf(client, "/login")
    import re
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    client.post("/login", data={
        "email": "adminr123@gmail.com",
        "password": "123456789",
        "csrf_token": token,
    })
    r = client.get("/lista")
    assert r.status_code == 200, f"/lista logueado -> {r.status_code}"
    print("OK  /lista logueado")

    # POST sin token CSRF -> debe ser rechazado (400)
    r = client.post("/registro/nuevo", data={
        "tipo": "Gasto", "descripcion": "x", "monto": "100", "categoria": "Prueba",
    })
    assert r.status_code == 400, f"POST sin CSRF -> {r.status_code}"
    print("OK  CSRF bloquea POST sin token")


def test_agendamiento_recibe_datos_y_csrf():
    """El endpoint recibe los campos del formulario y exige CSRF."""
    client = app.test_client()
    with client.session_transaction() as sesion:
        sesion["user_id"] = 1
        sesion["user_email"] = "demo@test.local"
        sesion["_csrf"] = "token-prueba"

    with patch("app.blueprints.notificaciones.crear_agendamiento") as guardar:
        guardar.return_value = (True, "Sesión agendada correctamente")
        respuesta = client.post("/agendamiento", data={
            "csrf_token": "token-prueba",
            "fecha": "2099-01-01",
            "hora": "10:00",
            "categoria": "reserva",
            "estado": "pendiente",
            "comentarios": "Aprender a ahorrar",
        })

    assert respuesta.status_code == 200
    assert respuesta.json["ok"] is True
    guardar.assert_called_once_with(
        1, "2099-01-01", "10:00", "reserva", "pendiente", "Aprender a ahorrar"
    )
    print("OK  agendamiento recibe datos + CSRF")


def test_panel_presupuesto_coherente():
    """El presupuesto del periodo y el total de gastos deben ser coherentes."""
    import re
    client = app.test_client()
    r = client.get("/login")
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    client.post("/login", data={
        "email": "adminr123@gmail.com",
        "password": "123456789",
        "csrf_token": token,
    }, follow_redirects=False)
    texto = client.get("/panel").get_data(as_text=True)
    assert "Presupuesto" in texto
    assert "% usado" in texto, "El panel no muestra el porcentaje de presupuesto"
    assert "$0Gastado" not in texto, "Presupuesto marca $0 gastado pese a existir gastos"
    print("OK  presupuesto del panel coherente")


def test_presupuesto_actualiza():
    """El usuario puede definir el presupuesto y el panel lo refleja."""
    import re
    client = login_demo(app.test_client())

    r = client.get("/presupuesto")
    assert r.status_code == 200, f"/presupuesto -> {r.status_code}"
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)

    r = client.post("/presupuesto", data={"monto": "350000", "csrf_token": token},
                    follow_redirects=False)
    assert r.status_code == 302, f"POST /presupuesto -> {r.status_code}"
    assert "ok=" in r.headers["Location"], "No confirmó el guardado"

    panel = client.get("/panel").get_data(as_text=True)
    assert "$350.000" in panel, "El panel no refleja el presupuesto guardado"

    r = client.post("/presupuesto", data={"monto": "0", "csrf_token": token},
                    follow_redirects=False)
    assert r.status_code == 302, f"POST /presupuesto inválido -> {r.status_code}"
    assert "error=" in r.headers["Location"], "No rechazó un monto inválido"
    print("OK  presupuesto se define y valida")


def test_perfil_actualiza_datos_y_password():
    """El perfil permite editar datos, rechaza duplicados y cambia la contraseña."""
    import re
    from urllib.parse import unquote

    unique = uuid.uuid4().hex[:8]
    email = f"perfil_{unique}@test.local"
    username = f"perfil_{unique}"
    password = "12345678x"

    client = app.test_client()
    r = client.get("/registro")
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    r = client.post("/registro", data={
        "full_name": "Perfil Test",
        "email": email,
        "username": username,
        "password": password,
        "confirm_password": password,
        "user_type": "estudiante",
        "csrf_token": token,
    }, follow_redirects=True)
    assert "Cuenta creada correctamente" in r.get_data(as_text=True)

    r = client.get("/login")
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    r = client.post("/login", data={
        "email": email,
        "password": password,
        "csrf_token": token,
    }, follow_redirects=False)
    assert r.status_code == 302, f"login de perfil -> {r.status_code}"

    r = client.get("/perfil")
    assert r.status_code == 200, f"/perfil -> {r.status_code}"
    texto = r.get_data(as_text=True)
    assert username in texto and email in texto, "El perfil no muestra los datos de la cuenta"
    token = re.search(r'name="csrf_token" value="([^"]+)"', texto).group(1)

    nuevo_username = f"perfilnew_{unique}"
    r = client.post("/perfil", data={
        "nombre": "Perfil Editado",
        "username": nuevo_username,
        "csrf_token": token,
    }, follow_redirects=False)
    assert r.status_code == 302, f"POST /perfil -> {r.status_code}"
    assert "ok=" in r.headers["Location"], "No confirmó la actualización"
    r = client.get("/perfil")
    texto = r.get_data(as_text=True)
    assert "Perfil Editado" in texto and nuevo_username in texto, "Los datos no persisten"

    r = client.post("/perfil", data={
        "nombre": "Perfil Editado",
        "username": "adminrdv",
        "csrf_token": token,
    }, follow_redirects=False)
    assert r.status_code == 302, f"POST /perfil duplicado -> {r.status_code}"
    assert "error=" in r.headers["Location"], "No rechazó el usuario duplicado"
    assert "ya está en uso" in unquote(r.headers["Location"]), \
        "No devolvió el mensaje de usuario duplicado"

    r = client.post("/perfil/password", data={
        "actual": "incorrecta",
        "nueva": "nuevaClave123",
        "confirmar": "nuevaClave123",
        "csrf_token": token,
    }, follow_redirects=False)
    assert r.status_code == 302, f"POST /perfil/password inválido -> {r.status_code}"
    assert "error=" in r.headers["Location"], "No rechazó la contraseña actual incorrecta"
    assert "contraseña actual es incorrecta" in unquote(r.headers["Location"]), \
        "No devolvió el mensaje de contraseña incorrecta"

    r = client.post("/perfil/password", data={
        "actual": password,
        "nueva": "nuevaClave123",
        "confirmar": "nuevaClave123",
        "csrf_token": token,
    }, follow_redirects=False)
    assert r.status_code == 302, f"POST /perfil/password -> {r.status_code}"
    assert "ok=" in r.headers["Location"], "No confirmó el cambio de contraseña"

    nuevo_client = app.test_client()
    r = nuevo_client.get("/login")
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    r = nuevo_client.post("/login", data={
        "email": email,
        "password": "nuevaClave123",
        "csrf_token": token,
    }, follow_redirects=False)
    assert r.status_code == 302, "La nueva contraseña no permite iniciar sesión"
    print("OK  perfil actualiza datos, rechaza duplicado y cambia contraseña")


def test_movimiento_crea_y_elimina():
    """Crea y elimina un gasto real, verificando su persistencia en /lista."""
    import re

    client = app.test_client()
    email, password = crear_cuenta_prueba(client)
    login_usuario(client, email, password)

    r = client.get("/lista")
    assert r.status_code == 200, f"/lista -> {r.status_code}"
    texto = r.get_data(as_text=True)
    token = re.search(r'name="csrf_token" value="([^"]+)"', texto).group(1)

    descripcion = f"Movimiento RNF10 {uuid.uuid4().hex[:8]}"
    r = client.post("/registro/nuevo", data={
        "tipo": "Gasto",
        "descripcion": descripcion,
        "monto": "12345",
        "categoria": "Prueba RNF-10",
        "csrf_token": token,
    }, follow_redirects=False)
    assert r.status_code == 302, f"POST /registro/nuevo -> {r.status_code}"
    assert "ok=" in r.headers["Location"], "No confirmó la creación del movimiento"

    texto = client.get("/lista").get_data(as_text=True)
    assert descripcion in texto, "El movimiento creado no aparece en /lista"
    assert "$12.345" in texto, "El monto del movimiento no aparece formateado"

    coincidencia = re.search(r"/registro/eliminar/Gasto/(\d+)", texto)
    assert coincidencia, "No se encontró el formulario de eliminación del movimiento"
    registro_id = coincidencia.group(1)
    token = re.search(r'name="csrf_token" value="([^"]+)"', texto).group(1)

    r = client.post(f"/registro/eliminar/Gasto/{registro_id}", data={
        "csrf_token": token,
    }, follow_redirects=False)
    assert r.status_code == 302, f"POST eliminar -> {r.status_code}"
    assert "ok=" in r.headers["Location"], "No confirmó la eliminación del movimiento"

    texto = client.get("/lista").get_data(as_text=True)
    assert descripcion not in texto, "El movimiento eliminado sigue apareciendo en /lista"
    print("OK  movimiento real se crea, persiste y se elimina")


def test_login_bloquea_tras_cinco_fallos():
    """Cinco fallos bloquean el login incluso con la contraseña correcta."""
    import re

    client = app.test_client()
    email, password = crear_cuenta_prueba(client)

    r = client.get("/login")
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)

    for intento in range(1, 6):
        r = client.post("/login", data={
            "email": email,
            "password": "incorrecta",
            "csrf_token": token,
        }, follow_redirects=False)
        assert r.status_code == 200, f"intento {intento} -> {r.status_code}"
        if intento < 5:
            assert "Correo o contraseña incorrectos" in r.get_data(as_text=True)

    r = client.post("/login", data={
        "email": email,
        "password": password,
        "csrf_token": token,
    }, follow_redirects=False)
    assert r.status_code == 200, "El intento bloqueado no debe redirigir al panel"
    texto = r.get_data(as_text=True)
    assert "Demasiados intentos fallidos" in texto, "No se activó el bloqueo tras 5 fallos"
    assert "Espera" in texto and "segundos" in texto, "El bloqueo no indica el tiempo de espera"
    print("OK  login se bloquea tras 5 intentos fallidos")


def test_logout_requiere_post_y_csrf():
    """Cerrar sesión no debe cambiar estado mediante GET ni sin CSRF."""
    client = app.test_client()
    with client.session_transaction() as sesion:
        sesion["user_email"] = "demo@test.local"
        sesion["_csrf"] = "token-prueba"

    assert client.get("/logout").status_code == 405
    respuesta = client.post("/logout")
    assert respuesta.status_code == 400
    print("OK  logout exige POST + CSRF")


def test_notificaciones_autenticado():
    """El centro de notificaciones se renderiza para la cuenta demo."""
    client = login_demo(app.test_client())
    r = client.get("/notificacion")
    assert r.status_code == 200, f"/notificacion logueado -> {r.status_code}"
    texto = r.get_data(as_text=True)
    assert "Notificaciones" in texto, "La página no muestra el título de notificaciones"
    assert "Iniciar Sesión" not in texto, "Se renderizó el login en lugar de notificaciones"
    assert "Sin notificaciones por ahora" in texto or "notif-card" in texto, \
        "No se muestra ni el estado vacío ni las tarjetas de notificación"
    print("OK  /notificacion autenticado")


def test_agendamiento_validacion():
    """El agendamiento rechaza fecha, hora y categoría inválidas."""
    client = app.test_client()
    with client.session_transaction() as sesion:
        sesion["user_id"] = 1
        sesion["user_email"] = "demo@test.local"
        sesion["_csrf"] = "token-prueba"

    base = {
        "csrf_token": "token-prueba",
        "fecha": "2099-01-01",
        "hora": "10:00",
        "categoria": "reserva",
        "comentarios": "",
    }
    casos = (
        ({"categoria": "otra"}, "categoría"),
        ({"fecha": "2000-01-01"}, "anterior a hoy"),
        ({"hora": "99:99"}, "formato"),
        ({"fecha": "01/01/2099"}, "formato"),
    )
    for cambios, esperado in casos:
        datos = {**base, **cambios}
        r = client.post("/agendamiento", data=datos)
        assert r.status_code == 400, f"{cambios} -> {r.status_code}"
        assert r.json["ok"] is False, f"{cambios} no devolvió ok=False"
        assert esperado in r.json["mensaje"], f"{cambios} -> {r.json['mensaje']}"
    print("OK  agendamiento valida fecha, hora y categoría")


def test_agendamiento_sin_sesion():
    """El agendamiento no se puede usar sin sesión iniciada."""
    import re
    client = app.test_client()
    r = client.get("/login")
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    r = client.post("/agendamiento", data={"csrf_token": token, "fecha": "2099-01-01"})
    assert r.status_code == 302, f"POST /agendamiento sin sesión -> {r.status_code}"
    assert "/login" in r.headers["Location"], "No redirige a login"
    print("OK  agendamiento exige sesión")


def test_lista_filtros_y_paginacion():
    """RF-15: los filtros y la paginación se resuelven en el servidor."""
    import re

    client = app.test_client()
    email, password = crear_cuenta_prueba(client)
    login_usuario(client, email, password)
    texto = client.get("/lista").get_data(as_text=True)
    token = re.search(r'name="csrf_token" value="([^"]+)"', texto).group(1)
    sufijo = uuid.uuid4().hex[:6]

    def crear(descripcion, tipo, monto=1000):
        """Envía un movimiento de prueba y exige que el servidor lo acepte."""
        r = client.post("/registro/nuevo", data={
            "tipo": tipo,
            "descripcion": descripcion,
            "monto": str(monto),
            "categoria": "Prueba RF-15",
            "csrf_token": token,
        }, follow_redirects=False)
        assert r.status_code == 302 and "ok=" in r.headers["Location"]

    crear(f"Cafe filtro {sufijo}", "Gasto", 5000)
    crear(f"Bus filtro {sufijo}", "Gasto", 2000)
    crear(f"Mesada filtro {sufijo}", "Ingreso", 10000)

    texto = client.get(f"/lista?q=Cafe+filtro+{sufijo}").get_data(as_text=True)
    assert f"Cafe filtro {sufijo}" in texto
    assert f"Bus filtro {sufijo}" not in texto, "El filtro q no limitó los resultados"

    texto = client.get("/lista?tipo=Ingreso").get_data(as_text=True)
    assert f"Mesada filtro {sufijo}" in texto
    assert f"Cafe filtro {sufijo}" not in texto, "El filtro tipo no limitó los resultados"

    for indice in range(8):
        crear(f"Pagina {indice} {sufijo}", "Gasto")

    texto = client.get("/lista").get_data(as_text=True)
    assert "Página 1 de 2" in texto, "La lista no paginó de 10 en 10"
    texto = client.get("/lista?page=2").get_data(as_text=True)
    assert "Página 2 de 2" in texto, "La segunda página no está disponible"
    print("OK  RF-15 filtros y paginación en servidor")


def test_supervision_padre_vincula_y_desvincula():
    """RF-16: un padre solo consulta estudiantes vinculados por código."""
    import re

    estudiante = app.test_client()
    email_est, pass_est = crear_cuenta_prueba(estudiante, nombre="Estudiante Supervisado")
    login_usuario(estudiante, email_est, pass_est)

    perfil = estudiante.get("/perfil").get_data(as_text=True)
    coincidencia = re.search(r'perfil-codigo">\s*([A-Z0-9]{6,12})\s*<', perfil)
    assert coincidencia, "El perfil del estudiante no muestra el código de vinculación"
    codigo = coincidencia.group(1)

    padre = app.test_client()
    email_pad, pass_pad = crear_cuenta_prueba(padre, rol="padre", nombre="Padre Supervisor")
    login_usuario(padre, email_pad, pass_pad)

    texto = padre.get("/supervision").get_data(as_text=True)
    assert "Supervisión" in texto
    token = re.search(r'name="csrf_token" value="([^"]+)"', texto).group(1)

    r = padre.post("/supervision/vincular", data={
        "codigo": codigo, "csrf_token": token,
    }, follow_redirects=True)
    assert r.status_code == 200
    assert email_est in r.get_data(as_text=True), "El padre no ve al estudiante vinculado"

    enlace = re.search(r'/supervision/desvincular/(\d+)', r.get_data(as_text=True))
    assert enlace, "No aparece la acción de desvincular"
    r = padre.post(f"/supervision/desvincular/{enlace.group(1)}", data={
        "csrf_token": token,
    }, follow_redirects=True)
    assert email_est not in r.get_data(as_text=True), "El vínculo no se eliminó"

    r = estudiante.get("/supervision")
    assert r.status_code == 302 and "/panel" in r.headers["Location"], \
        "Un estudiante no debe acceder a la supervisión del padre"
    print("OK  RF-16 supervisión vincula y desvincula por código")


def test_bitacora_accesos_admin():
    """RF-17: el administrador ve los eventos y otros roles no."""
    client = login_demo(app.test_client())
    r = client.get("/bitacora")
    assert r.status_code == 200, f"/bitacora admin -> {r.status_code}"
    texto = r.get_data(as_text=True)
    assert "Bitácora de accesos" in texto
    assert "Inicio de sesión correcto" in texto, "No se registró el login correcto"

    estudiante = app.test_client()
    email, password = crear_cuenta_prueba(estudiante)
    login_usuario(estudiante, email, password)
    r = estudiante.get("/bitacora")
    assert r.status_code == 302 and "/panel" in r.headers["Location"], \
        "Un estudiante no debe acceder a la bitácora"
    print("OK  RF-17 bitácora registra y restringe accesos")


def test_recuperacion_password_token_un_uso():
    """RF-18: el enlace se solicita, cambia la contraseña y no se reutiliza."""
    import re
    from app.modelos.recuperacion import buscar_usuario_por_email, crear_token_recuperacion

    client = app.test_client()
    email, _ = crear_cuenta_prueba(client)

    r = client.get("/recuperar")
    token_csrf = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    r = client.post("/recuperar", data={"email": email, "csrf_token": token_csrf})
    assert r.status_code == 200
    assert "Si el correo está registrado" in r.get_data(as_text=True)

    usuario = buscar_usuario_por_email(email)
    token = crear_token_recuperacion(usuario["id"], "127.0.0.1")
    assert token, "No se pudo generar el token de recuperación"

    r = client.get(f"/restablecer/{token}")
    assert r.status_code == 200, f"/restablecer/<token> -> {r.status_code}"
    token_csrf = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)

    nueva = "nuevaClave456"
    r = client.post(f"/restablecer/{token}", data={
        "nueva": nueva, "confirmar": nueva, "csrf_token": token_csrf,
    })
    assert r.status_code == 200
    assert "actualizada correctamente" in r.get_data(as_text=True)

    nuevo_client = app.test_client()
    login_usuario(nuevo_client, email, nueva)

    r = client.post(f"/restablecer/{token}", data={
        "nueva": "otraClave789", "confirmar": "otraClave789", "csrf_token": token_csrf,
    })
    assert "no es válido o ya expiró" in r.get_data(as_text=True), \
        "El token de recuperación se pudo reutilizar"
    print("OK  RF-18 recuperación de contraseña con token de un uso")


def test_reportes_genera_y_exporta_csv():
    """RF-12/RF-14: reportes en la app y exportación CSV de movimientos."""
    import re
    client = login_demo(app.test_client())

    r = client.get("/reportes")
    assert r.status_code == 200, f"/reportes -> {r.status_code}"
    texto = r.get_data(as_text=True)
    token = re.search(r'name="csrf_token" value="([^"]+)"', texto).group(1)

    r = client.post("/reportes/generar", data={"tipo": "Mensual", "csrf_token": token},
                    follow_redirects=False)
    assert r.status_code == 302, f"POST /reportes/generar -> {r.status_code}"
    assert "ok=" in r.headers["Location"], "No confirmó la generación del reporte"

    texto = client.get("/reportes").get_data(as_text=True)
    assert "Mensual" in texto, "El reporte generado no aparece en el historial"

    r = client.get("/exportar")
    assert r.status_code == 200, f"GET /exportar -> {r.status_code}"
    assert r.mimetype == "text/csv", f"/exportar mimetype -> {r.mimetype}"
    contenido = r.get_data(as_text=True)
    assert "Tipo,Descripcion,Monto,Fecha,Categoria" in contenido, "El CSV no tiene cabecera"
    assert "Ingreso" in contenido or "Gasto" in contenido, "El CSV no trae movimientos del demo"
    print("OK  RF-12/RF-14 reportes en la app y exportación CSV")


if __name__ == "__main__":
    test_publicas()
    test_protegidas_sin_sesion()
    test_aliases_login_registro_html()
    test_registro()
    test_login_panel()
    test_lista_y_csrf()
    test_agendamiento_recibe_datos_y_csrf()
    test_panel_presupuesto_coherente()
    test_presupuesto_actualiza()
    test_notificaciones_autenticado()
    test_agendamiento_validacion()
    test_agendamiento_sin_sesion()
    test_perfil_actualiza_datos_y_password()
    test_movimiento_crea_y_elimina()
    test_login_bloquea_tras_cinco_fallos()
    test_logout_requiere_post_y_csrf()
    test_lista_filtros_y_paginacion()
    test_supervision_padre_vincula_y_desvincula()
    test_bitacora_accesos_admin()
    test_recuperacion_password_token_un_uso()
    test_reportes_genera_y_exporta_csv()
    print("\nTodos los smoke tests v10 pasaron.")
