from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlmodel import Session, select

from db import create_all_tables, get_session
from routers import peliculas, personajes, directores, curiosidades
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