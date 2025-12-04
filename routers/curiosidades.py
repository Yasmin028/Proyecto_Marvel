from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from db import get_session
from models.models import Curiosidad, Pelicula
from models.schemas import CuriosidadCreate

router = APIRouter()
SessionDep = Depends(get_session)

templates = Jinja2Templates(directory="templates")

# ------------------- CRUD Curiosidades -------------------

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

    return {"mensaje": "Curiosidad creada correctamente", "id": curiosidad.id}

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

    return {"mensaje": "Curiosidad actualizada correctamente"}

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

# ------------------- Vista HTML -------------------

@router.get("/page", response_class=HTMLResponse, tags=["Curiosidades"])
def vista_curiosidades(request: Request, session: Session = SessionDep):
    curiosidades = session.exec(select(Curiosidad).where(Curiosidad.estado == True)).all()
    return templates.TemplateResponse("curiosidades.html", {
        "request": request,
        "curiosidades": curiosidades
    })
    
@router.get("/{id}/page", response_class=HTMLResponse, tags=["Curiosidades"])
def detalle_curiosidad_html(id: int, request: Request, session: Session = SessionDep):
    curiosidad = session.get(Curiosidad, id)
    if not curiosidad:
        raise HTTPException(status_code=404, detail="Curiosidad no encontrada")

    return templates.TemplateResponse("curiosidad_detalle.html", {
        "request": request,
        "curiosidad": curiosidad
    })