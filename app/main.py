from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Generador de Recetas")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return {"message": "API Generador de Recetas"}


@app.get("/health")
def health():
    return {"status": "ok"}
