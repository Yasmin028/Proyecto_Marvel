import os, uuid
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from db import get_session
from models.models import Pelicula, Personaje, Director
from models.schemas import PeliculaCreate

router = APIRouter()
SessionDep = Depends(get_session)

UPLOAD_DIR = "static/img/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")

# ------------------- Vista HTML -------------------

@router.get("/page", response_class=HTMLResponse, tags=["Peliculas"])
def vista_peliculas(request: Request, mensaje: str = "", mensaje_error: str = "", session: Session = SessionDep):
    peliculas = session.exec(select(Pelicula).where(Pelicula.estado == True)).all()
    directores = session.exec(select(Director).where(Director.estado == True)).all()
    return templates.TemplateResponse("peliculas.html", {
        "request": request,
        "peliculas": peliculas,
        "directores": directores,
        "mensaje": mensaje,
        "mensaje_error": mensaje_error
    })

@router.get("/{id}/page", response_class=HTMLResponse, tags=["Peliculas"])
def detalle_pelicula_html(id: int, request: Request, session: Session = SessionDep):
    pelicula = session.get(Pelicula, id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return templates.TemplateResponse("pelicula_detalle.html", {
        "request": request,
        "pelicula": pelicula
    })

# ------------------- CRUD Películas -------------------

@router.get("/", tags=["Peliculas"])
def obtener_peliculas(activos: bool = True, session: Session = SessionDep):
    peliculas = session.exec(select(Pelicula).where(Pelicula.estado == activos)).all()
    return [
        {
            "id": p.id,
            "titulo": p.titulo,
            "año": p.año,
            "estado": p.estado,
            "imagen_url": p.imagen_url,
            "director_id": p.director_id
        }
        for p in peliculas
    ]

@router.post("/", tags=["Peliculas"])
async def crear_pelicula(
    titulo: str = Form(...),
    año: int = Form(...),
    director_id: int = Form(None),
    imagen: UploadFile = File(None),
    session: Session = SessionDep
):
    # ✅ VALIDACIÓN DEL AÑO
    if año < 1900 or año > 2100:
        return RedirectResponse(
            url="/peliculas/page?mensaje_error=Año inválido. Debe estar entre 1900 y 2100.",
            status_code=303
        )

    # ✅ Validar si ya existe
    existe = session.exec(select(Pelicula).where(Pelicula.titulo == titulo)).first()
    if existe:
        return RedirectResponse(
            url="/peliculas/page?mensaje_error=La película ya existe con ese título.",
            status_code=303
        )

    imagen_url = None
    imagen_data = None

    if imagen and imagen.filename:
        if imagen.content_type not in {"image/png", "image/jpeg", "image/webp"}:
            return RedirectResponse(
                url="/peliculas/page?mensaje_error=Formato de imagen no soportado. Usa PNG, JPEG o WEBP.",
                status_code=303
            )

        content = await imagen.read()
        imagen_data = content

        filename = f"{uuid.uuid4()}_{imagen.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(content)

        imagen_url = f"/static/img/uploads/{filename}"

    payload = PeliculaCreate(
        titulo=titulo,
        año=año,
        imagen_url=imagen_url
    )

    nueva = Pelicula(
        **payload.dict(),
        imagen_data=imagen_data,
        director_id=director_id
    )

    session.add(nueva)
    session.commit()
    session.refresh(nueva)

    return RedirectResponse(
        url=f"/peliculas/page?mensaje=Película creada correctamente (ID: {nueva.id})",
        status_code=303
    )

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

    return {"mensaje": "Película actualizada correctamente"}

# ✅ Ruta POST para eliminar desde HTML
@router.post("/{id}", tags=["Peliculas"])
def eliminar_pelicula_html(id: int, method: str = Form(...), session: Session = SessionDep):
    if method == "delete":
        db_pelicula = session.get(Pelicula, id)
        if not db_pelicula:
            raise HTTPException(status_code=404, detail="Película no encontrada")

        db_pelicula.estado = False
        session.add(db_pelicula)
        session.commit()

        return RedirectResponse(
            url="/peliculas/page?mensaje=Película eliminada",
            status_code=303
        )

    raise HTTPException(status_code=400, detail="Método no permitido")

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
    personaje = session.exec(select(Personaje).where(Personaje.nombre == nombre)).first()

    if not pelicula or not personaje:
        raise HTTPException(status_code=404, detail="Película o personaje no encontrado")

    if personaje not in pelicula.personajes:
        pelicula.personajes.append(personaje)
        session.add(pelicula)
        session.commit()
        session.refresh(pelicula)

    return {"mensaje": f"Personaje {nombre} asignado correctamente"}

@router.delete("/{pelicula_id}/personajes/{nombre}", tags=["Peliculas-Personajes"])
def remover_personaje(pelicula_id: int, nombre: str, session: Session = SessionDep):
    pelicula = session.get(Pelicula, pelicula_id)
    personaje = session.exec(select(Personaje).where(Personaje.nombre == nombre)).first()

    if not pelicula or not personaje:
        raise HTTPException(status_code=404, detail="Película o personaje no encontrado")

    if personaje in pelicula.personajes:
        pelicula.personajes.remove(personaje)
        session.add(pelicula)
        session.commit()

    return {"mensaje": f"Personaje {nombre} removido de la película"}