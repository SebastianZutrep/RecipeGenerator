# Generador de Recetas

API FastAPI que genera recetas usando un LLM.

## Requisitos

- Python 3.12+
- Docker (opcional)

## Uso local

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`.

## Uso con Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest
```
