import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Ingrediente, Receta, Usuario
from app.schemas.schemas import RecetaOut
from app.services.auth_service import get_current_user
from app.services.llm_service import generar_receta

router = APIRouter()


@router.post("/generar", response_model=RecetaOut, status_code=status.HTTP_201_CREATED)
async def generar_receta_endpoint(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """
    Genera una receta a partir del inventario actual del usuario autenticado
    usando un modelo de lenguaje (LLM). La receta generada se almacena en la BD.
    """
    ingredientes_db = db.query(Ingrediente).filter(Ingrediente.usuario_id == usuario.id).all()
    if not ingredientes_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tienes ingredientes en tu inventario. Agrega ingredientes primero.",
        )

    ingredientes_dict = [
        {"nombre": i.nombre, "cantidad": i.cantidad, "unidad": i.unidad or ""}
        for i in ingredientes_db
    ]

    try:
        receta_datos = await generar_receta(ingredientes_dict)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    receta = Receta(
        nombre_plato=receta_datos["nombre_plato"],
        ingredientes_json=json.dumps(receta_datos["ingredientes"], ensure_ascii=False),
        pasos_preparacion=json.dumps(receta_datos["pasos_preparacion"], ensure_ascii=False),
        tiempo_estimado=receta_datos["tiempo_estimado"],
        nivel_dificultad=receta_datos["nivel_dificultad"],
        usuario_id=usuario.id,
    )
    db.add(receta)
    db.commit()
    db.refresh(receta)
    return receta


@router.get("/", response_model=List[RecetaOut])
def listar_recetas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Lista el historial de recetas generadas por el usuario autenticado."""
    return db.query(Receta).filter(Receta.usuario_id == usuario.id).order_by(Receta.creado_en.desc()).all()


@router.get("/{receta_id}", response_model=RecetaOut)
def obtener_receta(
    receta_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Obtiene el detalle de una receta específica."""
    receta = db.query(Receta).filter(
        Receta.id == receta_id,
        Receta.usuario_id == usuario.id
    ).first()
    if not receta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
    return receta


@router.delete("/{receta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_receta(
    receta_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Elimina una receta del historial del usuario."""
    receta = db.query(Receta).filter(
        Receta.id == receta_id,
        Receta.usuario_id == usuario.id
    ).first()
    if not receta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
    db.delete(receta)
    db.commit()
