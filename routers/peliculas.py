import os, uuid
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlmodel import Session, select
from db import get_session
from models.models import Pelicula, Personaje
from models.schemas import PeliculaCreate

router = APIRouter()
SessionDep = Depends(get_session)

# Carpeta donde se guardan las imágenes
UPLOAD_DIR = "static/img/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
# ------------------- CRUD Películas -------------------

@router.get("/", tags=["Peliculas"])
def obtener_peliculas(activos: bool = True, session: Session = SessionDep):
    statement = select(Pelicula).where(Pelicula.estado == activos)
    return session.exec(statement).all()

@router.post("/", tags=["Peliculas"])
async def crear_pelicula(
    titulo: str = Form(...),
    año: int = Form(...),
    director_nombre: str = Form(...),
    imagen: UploadFile = Form(...),
    session: Session = SessionDep
):
    # 🔹 Validación de duplicados
    existe = session.exec(
        select(Pelicula).where(
            (Pelicula.titulo == titulo) & (Pelicula.director_nombre == director_nombre)
        )
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="La película ya existe con ese título y director")

    imagen_url = None
    if imagen and imagen.filename:
        # Validar tipo de archivo
        if imagen.content_type not in {"image/png", "image/jpeg", "image/webp"}:
            raise HTTPException(status_code=400, detail="Formato de imagen no soportado")
        # Guardar archivo físico
        content = await imagen.read()
        filename = f"{uuid.uuid4()}_{imagen.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(content)
        # Generar URL pública
        imagen_url = f"/static/img/uploads/{filename}"

    # Crear payload validado
    payload = PeliculaCreate(
        titulo=titulo,
        año=año,
        director_nombre=director_nombre,
        imagen_url=imagen_url
    )

    nueva = Pelicula(**payload.dict())
    session.add(nueva)
    session.commit()
    session.refresh(nueva)
    return nueva

@router.put("/{id}", tags=["Peliculas"])
def actualizar_pelicula(id: int, pelicula: PeliculaCreate, session: Session = SessionDep):
    db_pelicula = session.get(Pelicula, id)
    if not db_pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    for key, value in pelicula.dict(exclude_unset=True).items():
        setattr(db_pelicula, key, value)
    session.add(db_pelicula)
    session.commit()
    session.refresh(db_pelicula)
    return db_pelicula

@router.delete("/{id}", tags=["Peliculas"])
def eliminar_pelicula(id: int, session: Session = SessionDep):
    db_pelicula = session.get(Pelicula, id)
    if not db_pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    db_pelicula.estado = False
    session.add(db_pelicula)
    session.commit()
    return {"mensaje": "Película eliminada (soft delete)"}

@router.post("/restaurar/{id}", tags=["Peliculas"])
def restaurar_pelicula(id: int, session: Session = SessionDep):
    db_pelicula = session.get(Pelicula, id)
    if not db_pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    db_pelicula.estado = True
    session.add(db_pelicula)
    session.commit()
    return {"mensaje": "Película restaurada"}

@router.get("/historico", tags=["Peliculas"])
def peliculas_eliminadas(session: Session = SessionDep):
    statement = select(Pelicula).where(Pelicula.estado == False)
    return session.exec(statement).all()

# ------------------- Relación Películas - Personajes -------------------

@router.post("/{pelicula_id}/personajes/{nombre}", tags=["Peliculas-Personajes"])
def asignar_personaje(pelicula_id: int, nombre: str, session: Session = SessionDep):
    pelicula = session.get(Pelicula, pelicula_id)
    personaje = session.get(Personaje, nombre)
    if not pelicula or not personaje:
        raise HTTPException(status_code=404, detail="Película o personaje no encontrado")
    if personaje not in pelicula.personajes:
        pelicula.personajes.append(personaje)
        session.add(pelicula)
        session.commit()
        session.refresh(pelicula)
    return pelicula

@router.delete("/{pelicula_id}/personajes/{nombre}", tags=["Peliculas-Personajes"])
def remover_personaje(pelicula_id: int, nombre: str, session: Session = SessionDep):
    pelicula = session.get(Pelicula, pelicula_id)
    personaje = session.get(Personaje, nombre)
    if not pelicula or not personaje:
        raise HTTPException(status_code=404, detail="Película o personaje no encontrado")
    if personaje in pelicula.personajes:
        pelicula.personajes.remove(personaje)
        session.add(pelicula)
        session.commit()
    return {"mensaje": f"Personaje {nombre} removido de la película"}