from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from db import get_session
from models.models import Pelicula, Personaje, Director

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/page", response_class=HTMLResponse, tags=["Dashboard"])
def dashboard_page(request: Request, session: Session = Depends(get_session)):

    peliculas = session.exec(select(Pelicula)).all()
    personajes = session.exec(select(Personaje)).all()
    directores = session.exec(select(Director)).all()

    # KPIs
    total_peliculas = len(peliculas)
    total_personajes = len(personajes)
    total_directores = len(directores)

    # Películas por año
    conteo_anio = {}
    for p in peliculas:
        if p.año:
            conteo_anio[p.año] = conteo_anio.get(p.año, 0) + 1

    peliculas_por_anio = {
        "labels": list(conteo_anio.keys()),
        "data": list(conteo_anio.values())
    }

    # Personajes activos vs eliminados
    activos = len(session.exec(select(Personaje).where(Personaje.estado == True)).all())
    eliminados = len(session.exec(select(Personaje).where(Personaje.estado == False)).all())
    estado_personajes = [activos, eliminados]

    # Películas por director
    labels = []
    data = []
    for d in directores:
        labels.append(d.nombre)
        data.append(len(d.peliculas))

    peliculas_por_director = {
        "labels": labels,
        "data": data
    }

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "peliculas_por_anio": peliculas_por_anio,
        "estado_personajes": estado_personajes,
        "peliculas_por_director": peliculas_por_director,
        "total_peliculas": total_peliculas,
        "total_personajes": total_personajes,
        "total_directores": total_directores
    })