from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Calificacion, Receta, Usuario
from app.schemas.schemas import CalificacionCreate, CalificacionOut
from app.services.auth_service import get_current_user

router = APIRouter()


@router.post("/{receta_id}", response_model=CalificacionOut, status_code=status.HTTP_201_CREATED)
def calificar_receta(
    receta_id: int,
    datos: CalificacionCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """
    Califica una receta del historial del usuario (1 a 5 estrellas).
    Solo se permite una calificación por receta; si ya existe, se actualiza.
    """
    receta = db.query(Receta).filter(
        Receta.id == receta_id,
        Receta.usuario_id == usuario.id
    ).first()
    if not receta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")

    existente = db.query(Calificacion).filter(
        Calificacion.receta_id == receta_id,
        Calificacion.usuario_id == usuario.id,
    ).first()

    if existente:
        existente.estrellas = datos.estrellas
        existente.comentario = datos.comentario
        db.commit()
        db.refresh(existente)
        return existente

    nueva = Calificacion(
        estrellas=datos.estrellas,
        comentario=datos.comentario,
        receta_id=receta_id,
        usuario_id=usuario.id,
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.get("/{receta_id}", response_model=CalificacionOut)
def ver_calificacion(
    receta_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Obtiene la calificación de una receta específica del usuario."""
    cal = db.query(Calificacion).filter(
        Calificacion.receta_id == receta_id,
        Calificacion.usuario_id == usuario.id,
    ).first()
    if not cal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calificación no encontrada")
    return cal
