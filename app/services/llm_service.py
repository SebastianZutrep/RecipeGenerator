import os


class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    async def generar_receta(self, ingredientes: list[str]) -> str:
        prompt = f"Genera una receta con: {', '.join(ingredientes)}"
        # Integrar aquí la API del LLM (OpenAI, Gemini, etc.)
        return prompt
