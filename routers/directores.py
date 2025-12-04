import os, uuid
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from db import get_session
from models.models import Director
from models.schemas import DirectorCreate

router = APIRouter()
SessionDep = Depends(get_session)

UPLOAD_DIR = "static/img/directores"
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")

# ------------------- CRUD Directores -------------------

@router.get("/", tags=["Directores"])
def obtener_directores(activos: bool = True, session: Session = SessionDep):
    statement = select(Director).where(Director.estado == activos)
    return session.exec(statement).all()

@router.post("/", tags=["Directores"])
async def crear_director(
    nombre: str = Form(...),
    biografia: str = Form(...),
    imagen: UploadFile = File(None),
    session: Session = SessionDep
):
    existe = session.exec(select(Director).where(Director.nombre == nombre)).first()
    if existe:
        raise HTTPException(status_code=400, detail="El director ya existe")

    imagen_url = None

    if imagen and imagen.filename:
        if imagen.content_type not in {"image/png", "image/jpeg", "image/webp"}:
            raise HTTPException(status_code=400, detail="Formato de imagen no soportado")

        content = await imagen.read()

        filename = f"{uuid.uuid4()}_{imagen.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(content)

        imagen_url = f"/static/img/directores/{filename}"

    payload = DirectorCreate(nombre=nombre, biografia=biografia, imagen_url=imagen_url)
    nuevo = Director(**payload.dict())
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)

    return {"mensaje": "Director creado correctamente", "id": nuevo.id}

@router.put("/{nombre}", tags=["Directores"])
def actualizar_director(nombre: str, director: DirectorCreate, session: Session = SessionDep):
    db_director = session.exec(select(Director).where(Director.nombre == nombre)).first()
    if not db_director:
        raise HTTPException(status_code=404, detail="Director no encontrado")

    for key, value in director.dict(exclude_unset=True).items():
        setattr(db_director, key, value)

    session.add(db_director)
    session.commit()
    session.refresh(db_director)

    return {"mensaje": "Director actualizado correctamente"}

@router.delete("/{nombre}", tags=["Directores"])
def eliminar_director(nombre: str, session: Session = SessionDep):
    db_director = session.exec(select(Director).where(Director.nombre == nombre)).first()
    if not db_director:
        raise HTTPException(status_code=404, detail="Director no encontrado")

    db_director.estado = False
    session.add(db_director)
    session.commit()

    return {"mensaje": "Director eliminado (soft delete)"}

@router.post("/restaurar/{nombre}", tags=["Directores"])
def restaurar_director(nombre: str, session: Session = SessionDep):
    db_director = session.exec(select(Director).where(Director.nombre == nombre)).first()
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

# ------------------- Vista HTML -------------------

@router.get("/page", response_class=HTMLResponse, tags=["Directores"])
def vista_directores(request: Request, session: Session = SessionDep):
    directores = session.exec(select(Director).where(Director.estado == True)).all()

    # ✅ Forzar carga de películas para cada director
    for director in directores:
        _ = director.peliculas

    return templates.TemplateResponse("directores.html", {
        "request": request,
        "directores": directores
    })

@router.get("/{nombre}/page", response_class=HTMLResponse, tags=["Directores"])
def detalle_director_html(nombre: str, request: Request, session: Session = SessionDep):
    director = session.exec(select(Director).where(Director.nombre == nombre)).first()
    if not director:
        raise HTTPException(status_code=404, detail="Director no encontrado")

    # ✅ Fuerza la carga de películas
    _ = director.peliculas  

    return templates.TemplateResponse("director_detalle.html", {
        "request": request,
        "director": director
    })