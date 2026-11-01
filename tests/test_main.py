from fastapi.testclient import TestClient

from app.main import app, STUDENTS

client = TestClient(app)


def setup_function():
    STUDENTS.clear()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_crear_y_obtener_estudiante():
    r = client.post("/students", json={"nombre": "Ana", "apellido": "Pérez", "correo": "ana@mail.com"})
    assert r.status_code == 201
    sid = r.json()["id"]
    r = client.get(f"/students/{sid}")
    assert r.status_code == 200
    assert r.json()["correo"] == "ana@mail.com"


def test_correo_repetido():
    data = {"nombre": "Ana", "apellido": "Pérez", "correo": "ana@mail.com"}
    client.post("/students", json=data)
    r = client.post("/students", json=data)
    assert r.status_code == 409


def test_correo_invalido():
    r = client.post("/students", json={"nombre": "Ana", "apellido": "Pérez", "correo": "ana"})
    assert r.status_code == 422


def test_estudiante_no_existe():
    r = client.get("/students/no-existe")
    assert r.status_code == 404
