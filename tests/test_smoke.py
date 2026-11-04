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


def test_publicas():
    """Las páginas públicas deben responder sin sesión con HTTP 200."""
    client = app.test_client()
    for url in ("/", "/login", "/registro", "/contacto.html", "/servicios.html"):
        r = client.get(url)
        assert r.status_code == 200, f"GET {url} -> {r.status_code}"
        print(f"OK  pública  {url}")


def test_protegidas_sin_sesion():
    """Las rutas privadas deben redirigir al login cuando no hay sesión."""
    client = app.test_client()
    for url in ("/panel", "/lista", "/presupuesto", "/notificacion", "/agendamiento"):
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
    test_logout_requiere_post_y_csrf()
    print("\nTodos los smoke tests v10 pasaron.")
