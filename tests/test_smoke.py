"""Smoke test de FinovaTech v9: rutas públicas, protegidas, login real y CSRF."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()
app.config["TESTING"] = True


def obtener_csrf(client, url="/login"):
    r = client.get(url)
    assert r.status_code == 200, f"GET {url} -> {r.status_code}"
    return r, None


def test_publicas():
    client = app.test_client()
    for url in ("/", "/login", "/registro", "/contacto.html", "/servicios.html"):
        r = client.get(url)
        assert r.status_code == 200, f"GET {url} -> {r.status_code}"
        print(f"OK  pública  {url}")


def test_protegidas_sin_sesion():
    client = app.test_client()
    for url in ("/panel", "/lista", "/notificacion", "/agendamiento"):
        r = client.get(url)
        assert r.status_code == 302, f"GET {url} sin sesión -> {r.status_code}"
        assert "/login" in r.headers["Location"], f"{url} no redirige a login"
        print(f"OK  protegida {url} -> redirige a login")


def test_registro():
    client = app.test_client()
    r, _ = obtener_csrf(client, "/registro")
    # Extraemos el token CSRF de la plantilla
    import re
    token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
    email = "smoke@test.local"
    r = client.post("/registro", data={
        "full_name": "Smoke Test",
        "email": email,
        "username": "smoketest",
        "password": "12345678x",
        "confirm_password": "12345678x",
        "user_type": "estudiante",
        "csrf_token": token,
    }, follow_redirects=True)
    assert r.status_code == 200
    assert "Cuenta creada correctamente" in r.get_data(as_text=True), "No creó la cuenta"
    print("OK  registro nuevo usuario")


def test_login_panel():
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