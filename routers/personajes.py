import os, uuid
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile
from sqlmodel import Session, select
from db import get_session
from models.models import Personaje, Pelicula
from models.schemas import PersonajeCreate

router = APIRouter()
SessionDep = Depends(get_session)

# Carpeta donde se guardan las imágenes de personajes
UPLOAD_DIR = "static/img/personajes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ------------------- CRUD Personajes -------------------

@router.get("/", tags=["Personajes"])
def obtener_personajes(activos: bool = True, session: Session = SessionDep):
    statement = select(Personaje).where(Personaje.estado == activos)
    return session.exec(statement).all()

@router.post("/", tags=["Personajes"])
async def crear_personaje(
    nombre: str = Form(...),
    poder: str = Form(...),
    imagen: UploadFile = Form(None),
    session: Session = SessionDep
):
    # 🔹 Validación de duplicados por nombre
    existe = session.exec(select(Personaje).where(Personaje.nombre == nombre)).first()
    if existe:
        raise HTTPException(status_code=400, detail="El personaje ya existe")

    imagen_url = None
    if imagen and imagen.filename:
        if imagen.content_type not in {"image/png", "image/jpeg", "image/webp"}:
            raise HTTPException(status_code=400, detail="Formato de imagen no soportado")
        content = await imagen.read()
        filename = f"{uuid.uuid4()}_{imagen.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(content)
        imagen_url = f"/static/img/personajes/{filename}"

    payload = PersonajeCreate(
        nombre=nombre,
        poder=poder,
        imagen_url=imagen_url
    )

    nuevo = Personaje(**payload.dict())
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo

@router.put("/{nombre}", tags=["Personajes"])
def actualizar_personaje(nombre: str, personaje: PersonajeCreate, session: Session = SessionDep):
    db_personaje = session.exec(select(Personaje).where(Personaje.nombre == nombre)).first()
    if not db_personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    for key, value in personaje.dict(exclude_unset=True).items():
        setattr(db_personaje, key, value)
    session.add(db_personaje)
    session.commit()
    session.refresh(db_personaje)
    return db_personaje

@router.delete("/{nombre}", tags=["Personajes"])
def eliminar_personaje(nombre: str, session: Session = SessionDep):
    db_personaje = session.exec(select(Personaje).where(Personaje.nombre == nombre)).first()
    if not db_personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    db_personaje.estado = False
    session.add(db_personaje)
    session.commit()
    return {"mensaje": "Personaje eliminado (soft delete)"}

@router.post("/restaurar/{nombre}", tags=["Personajes"])
def restaurar_personaje(nombre: str, session: Session = SessionDep):
    db_personaje = session.exec(select(Personaje).where(Personaje.nombre == nombre)).first()
    if not db_personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    db_personaje.estado = True
    session.add(db_personaje)
    session.commit()
    return {"mensaje": "Personaje restaurado"}

@router.get("/historico", tags=["Personajes"])
def personajes_eliminados(session: Session = SessionDep):
    statement = select(Personaje).where(Personaje.estado == False)
    return session.exec(statement).all()

# ------------------- Relación Personajes - Películas -------------------

@router.get("/{nombre}/peliculas", tags=["Personajes-Peliculas"])
def obtener_peliculas_de_personaje(nombre: str, session: Session = SessionDep):
    personaje = session.exec(select(Personaje).where(Personaje.nombre == nombre)).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return personaje.peliculas
