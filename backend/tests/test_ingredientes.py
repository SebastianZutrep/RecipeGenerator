"""
test_ingredientes.py — Pruebas del CRUD de ingredientes.

Cubre:
  - GET  /ingredientes/        → listar (requiere auth)
  - POST /ingredientes/        → crear
  - PUT  /ingredientes/{id}    → actualizar
  - DELETE /ingredientes/{id}  → eliminar
  - Acceso sin token → 401
"""
import pytest


class TestListarIngredientes:

    def test_listar_sin_autenticacion_devuelve_401(self, client):
        res = client.get("/ingredientes/")
        assert res.status_code == 401

    def test_listar_inventario_vacio(self, client, usuario_registrado):
        res = client.get("/ingredientes/", headers=usuario_registrado["headers"])
        assert res.status_code == 200
        assert res.json() == []

    def test_listar_muestra_ingredientes_del_usuario(self, client, usuario_registrado):
        client.post("/ingredientes/", headers=usuario_registrado["headers"],
                    json={"nombre": "Arroz", "cantidad": "500", "unidad": "g"})
        client.post("/ingredientes/", headers=usuario_registrado["headers"],
                    json={"nombre": "Pollo", "cantidad": "300", "unidad": "g"})
        res = client.get("/ingredientes/", headers=usuario_registrado["headers"])
        assert res.status_code == 200
        nombres = [i["nombre"] for i in res.json()]
        assert "Arroz" in nombres
        assert "Pollo" in nombres


class TestCrearIngrediente:

    def test_crear_ingrediente_exitoso(self, client, usuario_registrado):
        res = client.post("/ingredientes/", headers=usuario_registrado["headers"],
                          json={"nombre": "Tomate", "cantidad": "3", "unidad": "unidades"})
        assert res.status_code == 201
        data = res.json()
        assert data["nombre"] == "Tomate"
        assert data["cantidad"] == "3"
        assert data["unidad"] == "unidades"
        assert "id" in data

    def test_crear_ingrediente_sin_unidad(self, client, usuario_registrado):
        res = client.post("/ingredientes/", headers=usuario_registrado["headers"],
                          json={"nombre": "Sal", "cantidad": "al gusto"})
        assert res.status_code == 201
        assert res.json()["unidad"] is None

    def test_crear_ingrediente_nombre_vacio_devuelve_422(self, client, usuario_registrado):
        res = client.post("/ingredientes/", headers=usuario_registrado["headers"],
                          json={"nombre": "", "cantidad": "100g"})
        assert res.status_code == 422

    def test_crear_ingrediente_sin_autenticacion_devuelve_401(self, client):
        res = client.post("/ingredientes/",
                          json={"nombre": "Tomate", "cantidad": "3"})
        assert res.status_code == 401

    def test_ingredientes_son_privados_por_usuario(self, client):
        """Cada usuario solo ve sus propios ingredientes."""
        # Usuario A
        client.post("/auth/registro", json={"nombre": "A", "email": "a@test.com", "password": "pass"})
        token_a = client.post("/auth/login", json={"email": "a@test.com", "password": "pass"}).json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Usuario B
        client.post("/auth/registro", json={"nombre": "B", "email": "b@test.com", "password": "pass"})
        token_b = client.post("/auth/login", json={"email": "b@test.com", "password": "pass"}).json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        client.post("/ingredientes/", headers=headers_a, json={"nombre": "Ingrediente de A", "cantidad": "1"})

        res_b = client.get("/ingredientes/", headers=headers_b)
        nombres_b = [i["nombre"] for i in res_b.json()]
        assert "Ingrediente de A" not in nombres_b


class TestActualizarIngrediente:

    def test_actualizar_ingrediente_exitoso(self, client, usuario_registrado):
        crear = client.post("/ingredientes/", headers=usuario_registrado["headers"],
                            json={"nombre": "Cebolla", "cantidad": "2", "unidad": "unidades"})
        ing_id = crear.json()["id"]

        res = client.put(f"/ingredientes/{ing_id}", headers=usuario_registrado["headers"],
                         json={"cantidad": "5"})
        assert res.status_code == 200
        assert res.json()["cantidad"] == "5"
        assert res.json()["nombre"] == "Cebolla"  # nombre no cambió

    def test_actualizar_ingrediente_ajeno_devuelve_404(self, client, usuario_registrado):
        res = client.put("/ingredientes/99999", headers=usuario_registrado["headers"],
                         json={"cantidad": "10"})
        assert res.status_code == 404


class TestEliminarIngrediente:

    def test_eliminar_ingrediente_exitoso(self, client, usuario_registrado):
        crear = client.post("/ingredientes/", headers=usuario_registrado["headers"],
                            json={"nombre": "Ajo", "cantidad": "3"})
        ing_id = crear.json()["id"]

        res = client.delete(f"/ingredientes/{ing_id}", headers=usuario_registrado["headers"])
        assert res.status_code == 204

        # Verificar que ya no aparece en el listado
        lista = client.get("/ingredientes/", headers=usuario_registrado["headers"]).json()
        ids = [i["id"] for i in lista]
        assert ing_id not in ids

    def test_eliminar_ingrediente_inexistente_devuelve_404(self, client, usuario_registrado):
        res = client.delete("/ingredientes/99999", headers=usuario_registrado["headers"])
        assert res.status_code == 404
