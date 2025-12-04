import base64
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from db import get_session
from models.models import Pelicula, Personaje, Director, Curiosidad

router = APIRouter()
SessionDep = Depends(get_session)

# 👇 instancia de templates (necesaria aquí)
templates = Jinja2Templates(directory="templates")

# 👇 Filtro Jinja para convertir binario a base64
def b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")

templates.env.filters["b64encode"] = b64encode

@router.get("/buscar", tags=["Busqueda"], response_class=HTMLResponse)
def buscar(request: Request, q: str = Query("", min_length=1), session: Session = SessionDep):
    term = q.strip()

    peliculas = session.exec(
        select(Pelicula).where(Pelicula.titulo.ilike(f"%{term}%"))
    ).all()

    personajes = session.exec(
        select(Personaje).where(Personaje.nombre.ilike(f"%{term}%"))
    ).all()

    directores = session.exec(
        select(Director).where(Director.nombre.ilike(f"%{term}%"))
    ).all()

    curiosidades = session.exec(
        select(Curiosidad).where(Curiosidad.contenido.ilike(f"%{term}%"))
    ).all()

    return templates.TemplateResponse("buscar.html", {
        "request": request,
        "q": term,
        "peliculas": peliculas,
        "personajes": personajes,
        "directores": directores,
        "curiosidades": curiosidades,
        "mensaje": None if (peliculas or personajes or directores or curiosidades) else "Sin resultados."
    })