"""
test_recetas_calificaciones.py — Pruebas de los endpoints de recetas y calificaciones.

El LLM real se mockea con unittest.mock para que los tests sean rápidos,
deterministas y no dependan de una API key real.

Cubre:
  - POST /recetas/generar  → con inventario, sin inventario, LLM fallido
  - GET  /recetas/         → historial
  - GET  /recetas/{id}     → detalle
  - DELETE /recetas/{id}   → eliminar
  - POST /calificaciones/{id} → calificar
  - GET  /calificaciones/{id} → ver calificación
"""
import json
import pytest
from unittest.mock import patch, AsyncMock


# Receta de ejemplo que el mock del LLM siempre devuelve
RECETA_MOCK = {
    "nombre_plato": "Arroz con Pollo Criollo",
    "ingredientes": [
        {"nombre": "Pollo", "cantidad": "500", "unidad": "g"},
        {"nombre": "Arroz", "cantidad": "200", "unidad": "g"},
    ],
    "pasos_preparacion": [
        "Cortar el pollo.",
        "Sofreír con especias.",
        "Agregar arroz y cocinar.",
    ],
    "tiempo_estimado": "45 minutos",
    "nivel_dificultad": "Fácil",
}


def agregar_ingrediente(client, headers, nombre="Pollo", cantidad="500", unidad="g"):
    """Helper para agregar un ingrediente rápidamente."""
    return client.post("/ingredientes/", headers=headers,
                       json={"nombre": nombre, "cantidad": cantidad, "unidad": unidad})


class TestGenerarReceta:

    @patch("app.routers.recetas.generar_receta", new_callable=AsyncMock, return_value=RECETA_MOCK)
    def test_generar_receta_exitoso(self, mock_llm, client, usuario_registrado):
        agregar_ingrediente(client, usuario_registrado["headers"])
        res = client.post("/recetas/generar", headers=usuario_registrado["headers"])
        assert res.status_code == 201
        data = res.json()
        assert data["nombre_plato"] == "Arroz con Pollo Criollo"
        assert data["tiempo_estimado"] == "45 minutos"
        assert data["nivel_dificultad"] == "Fácil"
        assert "id" in data

    @patch("app.routers.recetas.generar_receta", new_callable=AsyncMock, return_value=RECETA_MOCK)
    def test_generar_receta_guarda_json_en_bd(self, mock_llm, client, usuario_registrado):
        """Los ingredientes y pasos deben guardarse como JSON válido."""
        agregar_ingrediente(client, usuario_registrado["headers"])
        res = client.post("/recetas/generar", headers=usuario_registrado["headers"])
        data = res.json()
        # Verificar que los campos JSON son parseables
        ingredientes = json.loads(data["ingredientes_json"])
        pasos = json.loads(data["pasos_preparacion"])
        assert isinstance(ingredientes, list)
        assert isinstance(pasos, list)
        assert len(pasos) == 3

    def test_generar_receta_sin_ingredientes_devuelve_400(self, client, usuario_registrado):
        """No se puede generar una receta con el inventario vacío."""
        res = client.post("/recetas/generar", headers=usuario_registrado["headers"])
        assert res.status_code == 400

    def test_generar_receta_sin_autenticacion_devuelve_401(self, client):
        res = client.post("/recetas/generar")
        assert res.status_code == 401

    @patch("app.routers.recetas.generar_receta", new_callable=AsyncMock,
           side_effect=RuntimeError("Proveedor LLM no disponible"))
    def test_generar_receta_llm_falla_devuelve_503(self, mock_llm, client, usuario_registrado):
        """Si el LLM falla, la API debe responder con 503."""
        agregar_ingrediente(client, usuario_registrado["headers"])
        res = client.post("/recetas/generar", headers=usuario_registrado["headers"])
        assert res.status_code == 503


class TestHistorialRecetas:

    def test_listar_sin_autenticacion_devuelve_401(self, client):
        res = client.get("/recetas/")
        assert res.status_code == 401

    def test_historial_vacio_al_inicio(self, client, usuario_registrado):
        res = client.get("/recetas/", headers=usuario_registrado["headers"])
        assert res.status_code == 200
        assert res.json() == []

    @patch("app.routers.recetas.generar_receta", new_callable=AsyncMock, return_value=RECETA_MOCK)
    def test_historial_muestra_recetas_generadas(self, mock_llm, client, usuario_registrado):
        agregar_ingrediente(client, usuario_registrado["headers"])
        client.post("/recetas/generar", headers=usuario_registrado["headers"])
        res = client.get("/recetas/", headers=usuario_registrado["headers"])
        assert res.status_code == 200
        assert len(res.json()) == 1
        assert res.json()[0]["nombre_plato"] == "Arroz con Pollo Criollo"

    @patch("app.routers.recetas.generar_receta", new_callable=AsyncMock, return_value=RECETA_MOCK)
    def test_obtener_receta_por_id(self, mock_llm, client, usuario_registrado):
        agregar_ingrediente(client, usuario_registrado["headers"])
        crear = client.post("/recetas/generar", headers=usuario_registrado["headers"])
        receta_id = crear.json()["id"]

        res = client.get(f"/recetas/{receta_id}", headers=usuario_registrado["headers"])
        assert res.status_code == 200
        assert res.json()["id"] == receta_id

    def test_obtener_receta_inexistente_devuelve_404(self, client, usuario_registrado):
        res = client.get("/recetas/99999", headers=usuario_registrado["headers"])
        assert res.status_code == 404

    @patch("app.routers.recetas.generar_receta", new_callable=AsyncMock, return_value=RECETA_MOCK)
    def test_eliminar_receta_exitoso(self, mock_llm, client, usuario_registrado):
        agregar_ingrediente(client, usuario_registrado["headers"])
        crear = client.post("/recetas/generar", headers=usuario_registrado["headers"])
        receta_id = crear.json()["id"]

        res = client.delete(f"/recetas/{receta_id}", headers=usuario_registrado["headers"])
        assert res.status_code == 204

        lista = client.get("/recetas/", headers=usuario_registrado["headers"]).json()
        assert all(r["id"] != receta_id for r in lista)

    def test_eliminar_receta_inexistente_devuelve_404(self, client, usuario_registrado):
        res = client.delete("/recetas/99999", headers=usuario_registrado["headers"])
        assert res.status_code == 404


class TestCalificaciones:

    @patch("app.routers.recetas.generar_receta", new_callable=AsyncMock, return_value=RECETA_MOCK)
    def test_calificar_receta_exitoso(self, mock_llm, client, usuario_registrado):
        agregar_ingrediente(client, usuario_registrado["headers"])
        receta_id = client.post("/recetas/generar",
                                headers=usuario_registrado["headers"]).json()["id"]

        res = client.post(f"/calificaciones/{receta_id}",
                          headers=usuario_registrado["headers"],
                          json={"estrellas": 5, "comentario": "Excelente"})
        assert res.status_code == 201
        data = res.json()
        assert data["estrellas"] == 5
        assert data["comentario"] == "Excelente"
        assert data["receta_id"] == receta_id

    @patch("app.routers.recetas.generar_receta", new_callable=AsyncMock, return_value=RECETA_MOCK)
    def test_calificar_actualiza_si_ya_existe(self, mock_llm, client, usuario_registrado):
        """Calificar una receta ya calificada debe actualizar la nota, no crear una nueva."""
        agregar_ingrediente(client, usuario_registrado["headers"])
        receta_id = client.post("/recetas/generar",
                                headers=usuario_registrado["headers"]).json()["id"]

        client.post(f"/calificaciones/{receta_id}",
                    headers=usuario_registrado["headers"],
                    json={"estrellas": 3})
        res = client.post(f"/calificaciones/{receta_id}",
                          headers=usuario_registrado["headers"],
                          json={"estrellas": 5})
        assert res.status_code == 201
        assert res.json()["estrellas"] == 5

    @patch("app.routers.recetas.generar_receta", new_callable=AsyncMock, return_value=RECETA_MOCK)
    def test_calificacion_estrellas_invalidas_devuelve_422(self, mock_llm, client, usuario_registrado):
        agregar_ingrediente(client, usuario_registrado["headers"])
        receta_id = client.post("/recetas/generar",
                                headers=usuario_registrado["headers"]).json()["id"]
        res = client.post(f"/calificaciones/{receta_id}",
                          headers=usuario_registrado["headers"],
                          json={"estrellas": 10})
        assert res.status_code == 422

    def test_calificar_receta_inexistente_devuelve_404(self, client, usuario_registrado):
        res = client.post("/calificaciones/99999",
                          headers=usuario_registrado["headers"],
                          json={"estrellas": 4})
        assert res.status_code == 404

    @patch("app.routers.recetas.generar_receta", new_callable=AsyncMock, return_value=RECETA_MOCK)
    def test_obtener_calificacion(self, mock_llm, client, usuario_registrado):
        agregar_ingrediente(client, usuario_registrado["headers"])
        receta_id = client.post("/recetas/generar",
                                headers=usuario_registrado["headers"]).json()["id"]
        client.post(f"/calificaciones/{receta_id}",
                    headers=usuario_registrado["headers"],
                    json={"estrellas": 4, "comentario": "Muy buena"})

        res = client.get(f"/calificaciones/{receta_id}",
                         headers=usuario_registrado["headers"])
        assert res.status_code == 200
        assert res.json()["estrellas"] == 4

    def test_obtener_calificacion_inexistente_devuelve_404(self, client, usuario_registrado):
        res = client.get("/calificaciones/99999", headers=usuario_registrado["headers"])
        assert res.status_code == 404
