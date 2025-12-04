from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlmodel import select
import base64

from db import create_all_tables
from routers import peliculas, personajes, directores, curiosidades, buscar, dashboard

# Configurar templates y estáticos
templates = Jinja2Templates(directory="templates")

# 👇 Filtro Jinja para convertir binario a base64
def b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")

templates.env.filters["b64encode"] = b64encode

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all_tables()
    yield

app = FastAPI(title="Marvel API", version="2.0", lifespan=lifespan)

# Montar carpeta static (Bulma, imágenes, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers API y vistas
app.include_router(peliculas.router, prefix="/peliculas", tags=["Peliculas"])
app.include_router(personajes.router, prefix="/personajes", tags=["Personajes"])
app.include_router(directores.router, prefix="/directores", tags=["Directores"])
app.include_router(curiosidades.router, prefix="/curiosidades", tags=["Curiosidades"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(buscar.router)

# ------------------- Ruta Home -------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})