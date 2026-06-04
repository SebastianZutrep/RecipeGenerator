<<<<<<< HEAD
=======
import os
import json
import httpx
from typing import List
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = os.getenv("LLM_MODEL", "mistralai/mistral-7b-instruct")


def construir_prompt(ingredientes: List[dict]) -> str:
    """
    Construye el prompt que se enviará al LLM a partir del inventario del usuario.
    """
    lista = "\n".join(
        f"- {ing['nombre']}: {ing['cantidad']} {ing.get('unidad', '')}".strip()
        for ing in ingredientes
    )
    prompt = f"""Eres un chef experto. El usuario tiene los siguientes ingredientes disponibles:

{lista}

Con SOLO esos ingredientes (puedes usar sal, pimienta y agua de forma libre), genera UNA receta completa.
Responde ÚNICAMENTE con un objeto JSON válido, sin texto adicional, sin comillas adicionales, con esta estructura exacta:

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
    Servicio principal: llama al LLM con el inventario del usuario y devuelve
    la receta estructurada como diccionario Python.
    """
    if not ingredientes:
        raise ValueError("El inventario de ingredientes está vacío. Agrega ingredientes antes de generar una receta.")

    prompt = construir_prompt(ingredientes)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("APP_URL", "http://localhost:8000"),
        "X-Title": "Generador de Recetas",
    }

    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(
            f"Error del proveedor LLM (status {response.status_code}): {response.text[:300]}"
        )

    data = response.json()
    try:
        contenido = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Respuesta inesperada del LLM: {e}\nRespuesta completa: {str(data)[:300]}")

    receta = parsear_respuesta_llm(contenido)
    return receta
>>>>>>> feature/llm-integration
