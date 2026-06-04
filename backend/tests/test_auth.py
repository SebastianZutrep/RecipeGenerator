"""
test_auth.py — Pruebas de los endpoints de autenticación.

Cubre:
  - POST /auth/registro: creación exitosa, email duplicado, campos faltantes
  - POST /auth/login: credenciales correctas e incorrectas, token JWT
  - GET  /auth/me: usuario autenticado, token inválido
"""
import pytest


class TestRegistro:

    def test_registro_exitoso_devuelve_201(self, client):
        res = client.post("/auth/registro", json={
            "nombre": "Ana García",
            "email": "ana@test.com",
            "password": "segura123",
        })
        assert res.status_code == 201

    def test_registro_devuelve_datos_del_usuario(self, client):
        res = client.post("/auth/registro", json={
            "nombre": "Carlos López",
            "email": "carlos@test.com",
            "password": "clave456",
        })
        data = res.json()
        assert data["email"] == "carlos@test.com"
        assert data["nombre"] == "Carlos López"
        assert "id" in data
        assert "hashed_password" not in data  # nunca exponer la contraseña

    def test_registro_email_duplicado_devuelve_400(self, client):
        payload = {"nombre": "Juan", "email": "juan@test.com", "password": "clave123"}
        client.post("/auth/registro", json=payload)
        res = client.post("/auth/registro", json=payload)
        assert res.status_code == 400
        assert "email" in res.json()["detail"].lower() or "existe" in res.json()["detail"].lower()

    def test_registro_email_invalido_devuelve_422(self, client):
        res = client.post("/auth/registro", json={
            "nombre": "Test",
            "email": "no-es-un-email",
            "password": "clave123",
        })
        assert res.status_code == 422

    def test_registro_sin_nombre_devuelve_422(self, client):
        res = client.post("/auth/registro", json={
            "email": "sin@nombre.com",
            "password": "clave123",
        })
        assert res.status_code == 422

    def test_registro_sin_password_devuelve_422(self, client):
        res = client.post("/auth/registro", json={
            "nombre": "Sin Pass",
            "email": "sinpass@test.com",
        })
        assert res.status_code == 422


class TestLogin:

    def test_login_exitoso_devuelve_token(self, client):
        client.post("/auth/registro", json={
            "nombre": "Pedro",
            "email": "pedro@test.com",
            "password": "mipass123",
        })
        res = client.post("/auth/login", json={
            "email": "pedro@test.com",
            "password": "mipass123",
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 20  # un JWT real tiene bastante longitud

    def test_login_password_incorrecta_devuelve_401(self, client):
        client.post("/auth/registro", json={
            "nombre": "María",
            "email": "maria@test.com",
            "password": "correcta",
        })
        res = client.post("/auth/login", json={
            "email": "maria@test.com",
            "password": "incorrecta",
        })
        assert res.status_code == 401

    def test_login_email_inexistente_devuelve_401(self, client):
        res = client.post("/auth/login", json={
            "email": "noexiste@test.com",
            "password": "cualquier",
        })
        assert res.status_code == 401

    def test_login_sin_campos_devuelve_422(self, client):
        res = client.post("/auth/login", json={})
        assert res.status_code == 422


class TestMe:

    def test_me_con_token_valido_devuelve_usuario(self, client, usuario_registrado):
        res = client.get("/auth/me", headers=usuario_registrado["headers"])
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == usuario_registrado["email"]
        assert data["nombre"] == usuario_registrado["nombre"]

    def test_me_sin_token_devuelve_401(self, client):
        res = client.get("/auth/me")
        assert res.status_code == 401

    def test_me_con_token_invalido_devuelve_401(self, client):
        res = client.get("/auth/me", headers={"Authorization": "Bearer token_falso"})
        assert res.status_code == 401
