"""Pruebas smoke del flujo principal de FinovaTech v9.

Comprueba que la aplicación pueda arrancar, que las rutas públicas respondan,
que las rutas privadas exijan autenticación y que los formularios respeten
la protección CSRF. Estas pruebas usan la base de datos configurada y la
cuenta demo, por lo que sirven como verificación rápida de integración local.
"""
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()
app.config["TESTING"] = True


def obtener_csrf(client, url="/login"):
    """Obtiene una página para inicializar la sesión y su token CSRF."""
    r = client.get(url)
    assert r.status_code == 200, f"GET {url} -> {r.status_code}"
    return r, None


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
    for url in ("/panel", "/lista", "/notificacion", "/agendamiento"):
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


if __name__ == "__main__":
    test_publicas()
    test_protegidas_sin_sesion()
    test_registro()
    test_login_panel()
    test_lista_y_csrf()
    print("\nTodos los smoke tests v9 pasaron.")