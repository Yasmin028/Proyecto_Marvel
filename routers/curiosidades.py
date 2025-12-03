from fastapi import APIRouter, Depends, HTTPException, Form
from sqlmodel import Session, select
from db import get_session
from models.models import Curiosidad, Pelicula
from models.schemas import CuriosidadCreate

router = APIRouter()
SessionDep = Depends(get_session)

@router.get("/", tags=["Curiosidades"])
def obtener_curiosidades(activos: bool = True, session: Session = SessionDep):
    statement = select(Curiosidad).where(Curiosidad.estado == activos)
    return session.exec(statement).all()

@router.post("/", tags=["Curiosidades"])
def crear_curiosidad(
    contenido: str = Form(...),
    pelicula_nombre: str = Form(...),
    session: Session = SessionDep
):
    pelicula = session.exec(select(Pelicula).where(Pelicula.titulo == pelicula_nombre)).first()
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")

    curiosidad = Curiosidad(contenido=contenido, pelicula_id=pelicula.id)
    session.add(curiosidad)
    session.commit()
    session.refresh(curiosidad)
    return curiosidad

@router.put("/{curiosidad_id}", tags=["Curiosidades"])
def actualizar_curiosidad(curiosidad_id: int, curiosidad: CuriosidadCreate, session: Session = SessionDep):
    db_curiosidad = session.get(Curiosidad, curiosidad_id)
    if not db_curiosidad:
        raise HTTPException(status_code=404, detail="Curiosidad no encontrada")
    for key, value in curiosidad.dict(exclude_unset=True).items():
        setattr(db_curiosidad, key, value)
    session.add(db_curiosidad)
    session.commit()
    session.refresh(db_curiosidad)
    return db_curiosidad

@router.delete("/{curiosidad_id}", tags=["Curiosidades"])
def eliminar_curiosidad(curiosidad_id: int, session: Session = SessionDep):
    db_curiosidad = session.get(Curiosidad, curiosidad_id)
    if not db_curiosidad:
        raise HTTPException(status_code=404, detail="Curiosidad no encontrada")
    db_curiosidad.estado = False
    session.add(db_curiosidad)
    session.commit()
    return {"mensaje": "Curiosidad eliminada (soft delete)"}

@router.post("/restaurar/{curiosidad_id}", tags=["Curiosidades"])
def restaurar_curiosidad(curiosidad_id: int, session: Session = SessionDep):
    db_curiosidad = session.get(Curiosidad, curiosidad_id)
    if not db_curiosidad:
        raise HTTPException(status_code=404, detail="Curiosidad no encontrada")
    db_curiosidad.estado = True
    session.add(db_curiosidad)
    session.commit()
    return {"mensaje": "Curiosidad restaurada"}

@router.get("/historico", tags=["Curiosidades"])
def curiosidades_eliminadas(session: Session = SessionDep):
    statement = select(Curiosidad).where(Curiosidad.estado == False)
    return session.exec(statement).all()