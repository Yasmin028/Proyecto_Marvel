from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlmodel import Session, select

from db import create_all_tables, get_session
from routers import peliculas, personajes, directores, curiosidades, buscar
from models.models import Pelicula, Personaje, Director, Curiosidad

# Configurar templates y estáticos
templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all_tables()
    yield

app = FastAPI(title="Marvel API", version="2.0", lifespan=lifespan)

# Montar carpeta static (Bulma, imágenes, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers API
app.include_router(peliculas.router, prefix="/peliculas", tags=["Peliculas"])
app.include_router(personajes.router, prefix="/personajes", tags=["Personajes"])
app.include_router(directores.router, prefix="/directores", tags=["Directores"])
app.include_router(curiosidades.router, prefix="/curiosidades", tags=["Curiosidades"])
app.include_router(buscar.router)   # 👈 ahora buscar.py maneja la ruta /buscar

# ------------------- Rutas HTML -------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/peliculas/page", response_class=HTMLResponse)
def peliculas_page(request: Request, session: Session = Depends(get_session)):
    items = session.exec(select(Pelicula)).all()
    return templates.TemplateResponse("peliculas.html", {"request": request, "peliculas": items})

@app.get("/personajes/page", response_class=HTMLResponse)
def personajes_page(request: Request, session: Session = Depends(get_session)):
    items = session.exec(select(Personaje)).all()
    return templates.TemplateResponse("personajes.html", {"request": request, "personajes": items})

@app.get("/directores/page", response_class=HTMLResponse)
def directores_page(request: Request, session: Session = Depends(get_session)):
    items = session.exec(select(Director)).all()
    return templates.TemplateResponse("directores.html", {"request": request, "directores": items})

@app.get("/curiosidades/page", response_class=HTMLResponse)
def curiosidades_page(request: Request, session: Session = Depends(get_session)):
    items = session.exec(select(Curiosidad)).all()
    return templates.TemplateResponse("curiosidades.html", {"request": request, "curiosidades": items})

# ------------------- Rutas Detalle -------------------

@app.get("/peliculas/{id}", response_class=HTMLResponse)
async def ver_pelicula(id: int, request: Request, session: Session = Depends(get_session)):
    pelicula = session.exec(select(Pelicula).where(Pelicula.id == id)).first()
    if not pelicula:
        return templates.TemplateResponse("404.html", {"request": request, "mensaje": "Película no encontrada"})
    return templates.TemplateResponse("pelicula_detalle.html", {"request": request, "pelicula": pelicula})

@app.get("/personajes/{nombre}", response_class=HTMLResponse)
async def ver_personaje(nombre: str, request: Request, session: Session = Depends(get_session)):
    personaje = session.exec(select(Personaje).where(Personaje.nombre == nombre)).first()
    if not personaje:
        return templates.TemplateResponse("404.html", {"request": request, "mensaje": "Personaje no encontrado"})
    return templates.TemplateResponse("personaje_detalle.html", {"request": request, "personaje": personaje})

@app.get("/directores/{nombre}", response_class=HTMLResponse)
async def ver_director(nombre: str, request: Request, session: Session = Depends(get_session)):
    director = session.exec(select(Director).where(Director.nombre == nombre)).first()
    if not director:
        return templates.TemplateResponse("404.html", {"request": request, "mensaje": "Director no encontrado"})
    return templates.TemplateResponse("director_detalle.html", {"request": request, "director": director})

@app.get("/curiosidades/{pelicula_id}", response_class=HTMLResponse)
async def ver_curiosidad(pelicula_id: int, request: Request, session: Session = Depends(get_session)):
    curiosidad = session.exec(select(Curiosidad).where(Curiosidad.pelicula_id == pelicula_id)).first()
    if not curiosidad:
        return templates.TemplateResponse("404.html", {"request": request, "mensaje": "Curiosidad no encontrada"})
    return templates.TemplateResponse("curiosidad_detalle.html", {"request": request, "curiosidad": curiosidad})