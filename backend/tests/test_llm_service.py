"""
test_llm_service.py — Pruebas del servicio de integración con el LLM.

Cubre:
  - construir_prompt(): que incluya los ingredientes y el formato JSON esperado
  - parsear_respuesta_llm(): JSON válido, inválido, con markdown, campos faltantes,
    ingredientes vacíos, pasos vacíos
"""
import json
import pytest

from app.services.llm_service import construir_prompt, parsear_respuesta_llm


# ── Fixtures de datos ─────────────────────────────────────────────────────────

INGREDIENTES_EJEMPLO = [
    {"nombre": "Pollo", "cantidad": "500", "unidad": "g"},
    {"nombre": "Arroz", "cantidad": "200", "unidad": "g"},
    {"nombre": "Tomate", "cantidad": "3", "unidad": "unidades"},
]

RECETA_VALIDA = {
    "nombre_plato": "Arroz con Pollo",
    "ingredientes": [
        {"nombre": "Pollo", "cantidad": "500", "unidad": "g"},
        {"nombre": "Arroz", "cantidad": "200", "unidad": "g"},
    ],
    "pasos_preparacion": [
        "Cortar el pollo en trozos medianos.",
        "Sofreír el tomate con cebolla durante 5 minutos.",
        "Agregar el pollo y cocinar 10 minutos.",
        "Incorporar el arroz con agua y cocinar 20 minutos.",
    ],
    "tiempo_estimado": "40 minutos",
    "nivel_dificultad": "Fácil",
}


# ── construir_prompt ──────────────────────────────────────────────────────────

class TestConstruirPrompt:

    def test_contiene_todos_los_ingredientes(self):
        prompt = construir_prompt(INGREDIENTES_EJEMPLO)
        assert "Pollo" in prompt
        assert "Arroz" in prompt
        assert "Tomate" in prompt

    def test_contiene_cantidades(self):
        prompt = construir_prompt(INGREDIENTES_EJEMPLO)
        assert "500" in prompt
        assert "200" in prompt
        assert "3" in prompt

    def test_solicita_formato_json(self):
        prompt = construir_prompt(INGREDIENTES_EJEMPLO)
        assert "JSON" in prompt

    def test_incluye_campos_requeridos_en_prompt(self):
        prompt = construir_prompt(INGREDIENTES_EJEMPLO)
        for campo in ["nombre_plato", "ingredientes", "pasos_preparacion",
                      "tiempo_estimado", "nivel_dificultad"]:
            assert campo in prompt, f"El campo '{campo}' falta en el prompt"

    def test_prompt_con_un_solo_ingrediente(self):
        prompt = construir_prompt([{"nombre": "Huevo", "cantidad": "2", "unidad": "unidades"}])
        assert "Huevo" in prompt
        assert len(prompt) > 50  # es un prompt de longitud razonable

    def test_prompt_sin_unidad_no_falla(self):
        """Un ingrediente sin unidad no debe romper la construcción del prompt."""
        prompt = construir_prompt([{"nombre": "Sal", "cantidad": "1", "unidad": ""}])
        assert "Sal" in prompt


# ── parsear_respuesta_llm ─────────────────────────────────────────────────────

class TestParsearRespuestaLLM:

    def test_json_valido_se_parsea_correctamente(self):
        resultado = parsear_respuesta_llm(json.dumps(RECETA_VALIDA))
        assert resultado["nombre_plato"] == "Arroz con Pollo"
        assert len(resultado["ingredientes"]) == 2
        assert len(resultado["pasos_preparacion"]) == 4
        assert resultado["tiempo_estimado"] == "40 minutos"
        assert resultado["nivel_dificultad"] == "Fácil"

    def test_json_invalido_lanza_value_error(self):
        with pytest.raises(ValueError, match="JSON válido"):
            parsear_respuesta_llm("esto no es json {{{")

    def test_json_con_markdown_se_parsea(self):
        """El LLM frecuentemente envuelve el JSON en bloques ```json ... ```"""
        respuesta = "```json\n" + json.dumps(RECETA_VALIDA) + "\n```"
        resultado = parsear_respuesta_llm(respuesta)
        assert resultado["nombre_plato"] == "Arroz con Pollo"

    def test_falta_campo_nombre_plato(self):
        datos = {k: v for k, v in RECETA_VALIDA.items() if k != "nombre_plato"}
        with pytest.raises(ValueError, match="campo requerido"):
            parsear_respuesta_llm(json.dumps(datos))

    def test_falta_campo_ingredientes(self):
        datos = {k: v for k, v in RECETA_VALIDA.items() if k != "ingredientes"}
        with pytest.raises(ValueError, match="campo requerido"):
            parsear_respuesta_llm(json.dumps(datos))

    def test_falta_campo_pasos(self):
        datos = {k: v for k, v in RECETA_VALIDA.items() if k != "pasos_preparacion"}
        with pytest.raises(ValueError, match="campo requerido"):
            parsear_respuesta_llm(json.dumps(datos))

    def test_falta_campo_tiempo(self):
        datos = {k: v for k, v in RECETA_VALIDA.items() if k != "tiempo_estimado"}
        with pytest.raises(ValueError, match="campo requerido"):
            parsear_respuesta_llm(json.dumps(datos))

    def test_falta_campo_dificultad(self):
        datos = {k: v for k, v in RECETA_VALIDA.items() if k != "nivel_dificultad"}
        with pytest.raises(ValueError, match="campo requerido"):
            parsear_respuesta_llm(json.dumps(datos))

    def test_ingredientes_lista_vacia_lanza_error(self):
        datos = {**RECETA_VALIDA, "ingredientes": []}
        with pytest.raises(ValueError, match="lista no vacía"):
            parsear_respuesta_llm(json.dumps(datos))

    def test_pasos_lista_vacia_lanza_error(self):
        datos = {**RECETA_VALIDA, "pasos_preparacion": []}
        with pytest.raises(ValueError, match="lista no vacía"):
            parsear_respuesta_llm(json.dumps(datos))

    def test_respuesta_vacia_lanza_error(self):
        with pytest.raises(ValueError):
            parsear_respuesta_llm("")

    def test_respuesta_es_string_no_objeto(self):
        with pytest.raises(ValueError):
            parsear_respuesta_llm('"solo un string"')
