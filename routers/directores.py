from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models.models import Director
from models.schemas import DirectorCreate

router = APIRouter()
SessionDep = Depends(get_session)

@router.get("/", tags=["Directores"])
def obtener_directores(activos: bool = True, session: Session = SessionDep):
    statement = select(Director).where(Director.estado == activos)
    return session.exec(statement).all()

@router.post("/", tags=["Directores"])
def crear_director(director: DirectorCreate, session: Session = SessionDep):
    nuevo = Director(**director.dict())
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo

@router.put("/{nombre}", tags=["Directores"])
def actualizar_director(nombre: str, director: Director, session: Session = SessionDep):
    db_director = session.get(Director, nombre)
    if not db_director:
        raise HTTPException(status_code=404, detail="Director no encontrado")
    for key, value in director.dict(exclude_unset=True).items():
        setattr(db_director, key, value)
    session.add(db_director)
    session.commit()
    session.refresh(db_director)
    return db_director

@router.delete("/{nombre}", tags=["Directores"])
def eliminar_director(nombre: str, session: Session = SessionDep):
    db_director = session.get(Director, nombre)
    if not db_director:
        raise HTTPException(status_code=404, detail="Director no encontrado")
    db_director.estado = False
    session.add(db_director)
    session.commit()
    return {"mensaje": "Director eliminado (soft delete)"}

@router.post("/restaurar/{nombre}", tags=["Directores"])
def restaurar_director(nombre: str, session: Session = SessionDep):
    db_director = session.get(Director, nombre)
    if not db_director:
        raise HTTPException(status_code=404, detail="Director no encontrado")
    db_director.estado = True
    session.add(db_director)
    session.commit()
    return {"mensaje": "Director restaurado"}

@router.get("/historico", tags=["Directores"])
def directores_eliminados(session: Session = SessionDep):
    statement = select(Director).where(Director.estado == False)
    return session.exec(statement).all()