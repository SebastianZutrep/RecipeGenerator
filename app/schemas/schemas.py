from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


# ── Auth ──────────────────────────────────────────────
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: str
    creado_en: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# ── Ingredientes ───────────────────────────────────────
class IngredienteCreate(BaseModel):
    nombre: str
    cantidad: str
    unidad: Optional[str] = None

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre del ingrediente no puede estar vacío")
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return v

    @field_validator("cantidad")
    @classmethod
    def cantidad_no_vacia(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("La cantidad no puede estar vacía")
        return v


class IngredienteUpdate(BaseModel):
    nombre: Optional[str] = None
    cantidad: Optional[str] = None
    unidad: Optional[str] = None


class IngredienteOut(BaseModel):
    id: int
    nombre: str
    cantidad: str
    unidad: Optional[str]
    usuario_id: int
    creado_en: datetime

    class Config:
        from_attributes = True


# ── Recetas ────────────────────────────────────────────
class IngredienteReceta(BaseModel):
    nombre: str
    cantidad: str
    unidad: Optional[str] = None


class RecetaOut(BaseModel):
    id: int
    nombre_plato: str
    ingredientes_json: str
    pasos_preparacion: str
    tiempo_estimado: str
    nivel_dificultad: str
    usuario_id: int
    creado_en: datetime

    class Config:
        from_attributes = True


# ── Calificaciones ─────────────────────────────────────
class CalificacionCreate(BaseModel):
    estrellas: int
    comentario: Optional[str] = None

    @field_validator("estrellas")
    @classmethod
    def estrellas_validas(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Las estrellas deben estar entre 1 y 5")
        return v


class CalificacionOut(BaseModel):
    id: int
    estrellas: int
    comentario: Optional[str]
    receta_id: int
    usuario_id: int
    creado_en: datetime

    class Config:
        from_attributes = True
