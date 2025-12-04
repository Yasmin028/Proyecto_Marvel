from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from sqlmodel import create_engine
import base64

from db import DATABASE_URL, create_all_tables
from routers import peliculas, personajes, directores, curiosidades, buscar, dashboard

# Configurar templates y estáticos
templates = Jinja2Templates(directory="templates")

# 👇 Filtro Jinja para convertir binario a base64
def b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")

templates.env.filters["b64encode"] = b64encode

# ✅ Crear engine aquí
engine = create_engine(DATABASE_URL, echo=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all_tables(engine)
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


# ============================================================
# ✅ ✅ ✅ MANEJO DE ERRORES EN UNA SOLA PLANTILLA
# ============================================================

# ✅ Handler para errores HTTP (404, 403, 401, etc.)
@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "codigo": exc.status_code,
            "titulo": f"Error {exc.status_code}",
            "mensaje": exc.detail,
            "volver_url": request.headers.get("referer", "/")
        },
        status_code=exc.status_code
    )

# ✅ Handler para errores de validación (formularios, tipos incorrectos)
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "codigo": 422,
            "titulo": "Datos inválidos",
            "mensaje": "Los datos enviados no son válidos.",
            "detalle": str(exc),
            "volver_url": request.headers.get("referer", "/")
        },
        status_code=422
    )

# ✅ Handler para errores inesperados (500)
@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "codigo": 500,
            "titulo": "Error interno",
            "mensaje": "Algo salió mal en el servidor.",
            "detalle": str(exc),
            "volver_url": request.headers.get("referer", "/")
        },
        status_code=500
    )