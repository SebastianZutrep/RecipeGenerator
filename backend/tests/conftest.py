"""
conftest.py — Fixtures compartidas entre todos los archivos de prueba.
pytest las carga automáticamente sin necesidad de importarlas.
"""
import os
import pytest

# CRÍTICO: esto debe ejecutarse ANTES de cualquier import de app.*
# para que SQLAlchemy tome la URL de SQLite y no la de MySQL.
os.environ["DATABASE_URL"] = "sqlite:///./test_temp.db"

from fastapi.testclient import TestClient
from app.database import engine, Base
from app.main import app


@pytest.fixture(autouse=True)
def limpiar_tablas():
    """
    Crea todas las tablas antes de cada test y las destruye al terminar.
    Garantiza que cada test parte de una BD limpia y vacía.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(limpiar_tablas):
    """
    Cliente HTTP de prueba con la app FastAPI completa.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def usuario_registrado(client):
    """
    Crea un usuario de prueba y devuelve sus credenciales + token JWT.
    Útil para tests que necesitan autenticación sin repetir el setup.
    """
    payload = {
        "nombre": "Usuario Test",
        "email": "test@recetas.com",
        "password": "password123",
    }
    client.post("/auth/registro", json=payload)
    login = client.post("/auth/login", json={
        "email": payload["email"],
        "password": payload["password"],
    })
    token = login.json()["access_token"]
    return {
        "email": payload["email"],
        "password": payload["password"],
        "nombre": payload["nombre"],
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }
