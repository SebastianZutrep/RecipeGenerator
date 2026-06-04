from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
<<<<<<< HEAD
=======

app = FastAPI(title="Generador de Recetas")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return {"message": "API Generador de Recetas"}


@app.get("/health")
def health():
    return {"status": "ok"}
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
>>>>>>> origin/main
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, ingredientes, recetas, calificaciones

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Generador de Recetas con Inventario",
    description="API para gestionar ingredientes y generar recetas con IA",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(ingredientes.router, prefix="/ingredientes", tags=["Ingredientes"])
app.include_router(recetas.router, prefix="/recetas", tags=["Recetas"])
app.include_router(calificaciones.router, prefix="/calificaciones", tags=["Calificaciones"])


@app.get("/", tags=["Root"])
def root():
<<<<<<< HEAD
    return {"mensaje": "API de Generador de Recetas funcionando correctamente"}
=======
    return {"mensaje": "API de Generador de Recetas funcionando correctamente"}
>>>>>>> origin/main
