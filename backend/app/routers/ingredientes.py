from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Ingrediente, Usuario
from app.schemas.schemas import IngredienteCreate, IngredienteOut, IngredienteUpdate
from app.services.auth_service import get_current_user

router = APIRouter()


@router.post("/", response_model=IngredienteOut, status_code=status.HTTP_201_CREATED)
def crear_ingrediente(
    datos: IngredienteCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Agrega un ingrediente al inventario del usuario autenticado."""
    ingrediente = Ingrediente(
        nombre=datos.nombre,
        cantidad=datos.cantidad,
        unidad=datos.unidad,
        usuario_id=usuario.id,
    )
    db.add(ingrediente)
    db.commit()
    db.refresh(ingrediente)
    return ingrediente


@router.get("/", response_model=List[IngredienteOut])
def listar_ingredientes(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Lista todos los ingredientes del usuario autenticado."""
    return db.query(Ingrediente).filter(Ingrediente.usuario_id == usuario.id).all()


@router.get("/{ingrediente_id}", response_model=IngredienteOut)
def obtener_ingrediente(
    ingrediente_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Obtiene un ingrediente por ID."""
    ing = db.query(Ingrediente).filter(
        Ingrediente.id == ingrediente_id,
        Ingrediente.usuario_id == usuario.id
    ).first()
    if not ing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingrediente no encontrado")
    return ing


@router.put("/{ingrediente_id}", response_model=IngredienteOut)
def actualizar_ingrediente(
    ingrediente_id: int,
    datos: IngredienteUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Actualiza un ingrediente existente del inventario."""
    ing = db.query(Ingrediente).filter(
        Ingrediente.id == ingrediente_id,
        Ingrediente.usuario_id == usuario.id
    ).first()
    if not ing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingrediente no encontrado")

    if datos.nombre is not None:
        ing.nombre = datos.nombre
    if datos.cantidad is not None:
        ing.cantidad = datos.cantidad
    if datos.unidad is not None:
        ing.unidad = datos.unidad

    db.commit()
    db.refresh(ing)
    return ing


@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ingrediente(
    ingrediente_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Elimina un ingrediente del inventario."""
    ing = db.query(Ingrediente).filter(
        Ingrediente.id == ingrediente_id,
        Ingrediente.usuario_id == usuario.id
    ).first()
    if not ing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingrediente no encontrado")
    db.delete(ing)
    db.commit()
