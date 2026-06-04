import os
import json
import httpx
from typing import List
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


def construir_prompt(ingredientes: List[dict]) -> str:
    lista = "\n".join(
        f"- {ing['nombre']}: {ing['cantidad']} {ing.get('unidad', '') or ''}".strip()
        for ing in ingredientes
    )
    prompt = f"""Eres un chef experto. El usuario tiene EXACTAMENTE estos ingredientes disponibles:

{lista}

REGLAS ESTRICTAS que debes cumplir sin excepción:
1. USA ÚNICAMENTE los ingredientes listados arriba. No puedes añadir ningún otro ingrediente.
2. Las cantidades en la receta NO pueden superar las cantidades indicadas por el usuario.
3. Puedes usar sal, pimienta y agua sin restricción.
4. Si un ingrediente no tiene unidad, es porque se cuenta en unidades (ej: 3 huevos).

Genera UNA sola receta completa con esos ingredientes.
Responde ÚNICAMENTE con un objeto JSON válido, sin texto adicional, con esta estructura exacta:

{{
  "nombre_plato": "string",
  "ingredientes": [
    {{"nombre": "string", "cantidad": "string", "unidad": "string"}}
  ],
  "pasos_preparacion": [
    "string"
  ],
  "tiempo_estimado": "string",
  "nivel_dificultad": "Fácil | Medio | Difícil"
}}"""
    return prompt
    

def parsear_respuesta_llm(respuesta_texto: str) -> dict:
    """
    Parsea la respuesta del LLM extrayendo el JSON de la receta.
    Lanza ValueError si la respuesta no tiene el formato esperado.
    """
    texto = respuesta_texto.strip()

    # Eliminar bloques de código markdown si los hay
    if texto.startswith("```"):
        lineas = texto.split("\n")
        texto = "\n".join(lineas[1:-1]) if len(lineas) > 2 else texto

    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ValueError(f"La respuesta del LLM no es JSON válido: {e}\nRespuesta: {texto[:300]}")

    if not isinstance(datos, dict):
        raise ValueError(f"Falta el campo requerido 'nombre_plato' en la respuesta del LLM")

    campos_requeridos = ["nombre_plato", "ingredientes", "pasos_preparacion", "tiempo_estimado", "nivel_dificultad"]
    for campo in campos_requeridos:
        if campo not in datos:
            raise ValueError(f"Falta el campo requerido '{campo}' en la respuesta del LLM")

    if not isinstance(datos["ingredientes"], list) or len(datos["ingredientes"]) == 0:
        raise ValueError("El campo 'ingredientes' debe ser una lista no vacía")

    if not isinstance(datos["pasos_preparacion"], list) or len(datos["pasos_preparacion"]) == 0:
        raise ValueError("El campo 'pasos_preparacion' debe ser una lista no vacía")

    return datos


async def generar_receta(ingredientes: List[dict]) -> dict:
    """
    Servicio principal: llama a OpenAI con el inventario del usuario y devuelve
    la receta estructurada como diccionario Python.
    """
    if not ingredientes:
        raise ValueError("El inventario de ingredientes está vacío. Agrega ingredientes antes de generar una receta.")

    prompt = construir_prompt(ingredientes)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000,
        "response_format": {"type": "json_object"},  # fuerza JSON puro — exclusivo de OpenAI
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OPENAI_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(
            f"Error de OpenAI (status {response.status_code}): {response.text[:300]}"
        )

    data = response.json()
    try:
        contenido = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Respuesta inesperada de OpenAI: {e}\nRespuesta completa: {str(data)[:300]}")

    receta = parsear_respuesta_llm(contenido)
    return receta
