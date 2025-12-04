from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from db import get_session
from models.models import Curiosidad, Pelicula
from models.schemas import CuriosidadCreate

router = APIRouter()
SessionDep = Depends(get_session)

templates = Jinja2Templates(directory="templates")

# ------------------- CRUD Curiosidades -------------------

@router.get("/", tags=["Curiosidades"])
def obtener_curiosidades(activos: bool = True, session: Session = SessionDep):
    statement = select(Curiosidad).where(Curiosidad.estado == activos)
    return session.exec(statement).all()

@router.post("/", tags=["Curiosidades"])
def crear_curiosidad(
    contenido: str = Form(...),
    pelicula_id: int = Form(...),
    session: Session = SessionDep
):
    # ✅ Validación de longitud
    if len(contenido) < 10:
        return RedirectResponse(
            url="/curiosidades/page?mensaje_error=La curiosidad es demasiado corta. Mínimo 10 caracteres.",
            status_code=303
        )

    if len(contenido) > 300:
        return RedirectResponse(
            url="/curiosidades/page?mensaje_error=La curiosidad es demasiado larga. Máximo 300 caracteres.",
            status_code=303
        )

    pelicula = session.get(Pelicula, pelicula_id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")

    curiosidad = Curiosidad(contenido=contenido, pelicula_id=pelicula.id)
    session.add(curiosidad)
    session.commit()
    session.refresh(curiosidad)

    # ✅ Redirigir con mensaje
    return RedirectResponse(
        url=f"/curiosidades/page?mensaje=Curiosidad creada correctamente (ID: {curiosidad.id})",
        status_code=303
    )

@router.put("/{curiosidad_id}", tags=["Curiosidades"])
def actualizar_curiosidad(curiosidad_id: int, curiosidad: CuriosidadCreate, session: Session = SessionDep):
    db_curiosidad = session.get(Curiosidad, curiosidad_id)
    if not db_curiosidad:
        raise HTTPException(status_code=404, detail="Curiosidad no encontrada")

    for key, value in curiosidad.dict(exclude_unset=True).items():
        setattr(db_curiosidad, key, value)

    session.add(db_curiosidad)
    session.commit()
    session.refresh(db_curiosidad)

    return {"mensaje": "Curiosidad actualizada correctamente"}

# ✅ Ruta POST para eliminar desde HTML
@router.post("/{curiosidad_id}", tags=["Curiosidades"])
def eliminar_curiosidad_html(curiosidad_id: int, method: str = Form(...), session: Session = SessionDep):
    if method == "delete":
        db_curiosidad = session.get(Curiosidad, curiosidad_id)
        if not db_curiosidad:
            raise HTTPException(status_code=404, detail="Curiosidad no encontrada")

        db_curiosidad.estado = False
        session.add(db_curiosidad)
        session.commit()

        return RedirectResponse(
            url="/curiosidades/page?mensaje=Curiosidad eliminada",
            status_code=303
        )

    raise HTTPException(status_code=400, detail="Método no permitido")

@router.post("/restaurar/{curiosidad_id}", tags=["Curiosidades"])
def restaurar_curiosidad(curiosidad_id: int, session: Session = SessionDep):
    db_curiosidad = session.get(Curiosidad, curiosidad_id)
    if not db_curiosidad:
        raise HTTPException(status_code=404, detail="Curiosidad no encontrada")

    db_curiosidad.estado = True
    session.add(db_curiosidad)
    session.commit()

    return {"mensaje": "Curiosidad restaurada"}

@router.get("/historico", tags=["Curiosidades"])
def curiosidades_eliminadas(session: Session = SessionDep):
    statement = select(Curiosidad).where(Curiosidad.estado == False)
    return session.exec(statement).all()

# ------------------- Vista HTML -------------------

@router.get("/page", response_class=HTMLResponse, tags=["Curiosidades"])
def vista_curiosidades(request: Request, mensaje: str = "", mensaje_error: str = "", session: Session = SessionDep):
    curiosidades = session.exec(select(Curiosidad).where(Curiosidad.estado == True)).all()
    peliculas = session.exec(select(Pelicula).where(Pelicula.estado == True)).all()

    return templates.TemplateResponse("curiosidades.html", {
        "request": request,
        "curiosidades": curiosidades,
        "peliculas": peliculas,
        "mensaje": mensaje,
        "mensaje_error": mensaje_error
    })

@router.get("/{id}/page", response_class=HTMLResponse, tags=["Curiosidades"])
def detalle_curiosidad_html(id: int, request: Request, session: Session = SessionDep):
    curiosidad = session.get(Curiosidad, id)
    if not curiosidad:
        raise HTTPException(status_code=404, detail="Curiosidad no encontrada")

    return templates.TemplateResponse("curiosidad_detalle.html", {
        "request": request,
        "curiosidad": curiosidad
    })