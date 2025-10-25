from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from db import create_all_tables, get_session
from models import Pelicula, Personaje, Director, Curiosidad
from contextlib import asynccontextmanager

SessionDep = Depends(get_session)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all_tables() 
    yield

app = FastAPI(
    title="API Marvel - FastAPI",
    version="1.0",
    lifespan=lifespan
)

# -------------------- CRUD Películas --------------------
@app.get("/peliculas", tags=["Peliculas"])
def obtener_peliculas(activos: bool = True, session: Session = SessionDep):
    statement = select(Pelicula).where(Pelicula.estado == activos)
    return session.exec(statement).all()

@app.post("/peliculas", tags=["Peliculas"])
def crear_pelicula(pelicula: Pelicula, session: Session = SessionDep):
    session.add(pelicula)
    session.commit()
    session.refresh(pelicula)
    return pelicula

@app.put("/peliculas/{id}", tags=["Peliculas"])
def actualizar_pelicula(id: int, pelicula: Pelicula, session: Session = SessionDep):
    db_pelicula = session.get(Pelicula, id)
    if not db_pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    for key, value in pelicula.dict(exclude_unset=True).items():
        setattr(db_pelicula, key, value)
    session.add(db_pelicula)
    session.commit()
    session.refresh(db_pelicula)
    return db_pelicula

@app.delete("/peliculas/{id}", tags=["Peliculas"])
def eliminar_pelicula(id: int, session: Session = SessionDep):
    db_pelicula = session.get(Pelicula, id)
    if not db_pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    db_pelicula.estado = False  # Soft delete
    session.add(db_pelicula)
    session.commit()
    return {"mensaje": "Película eliminada (soft delete)"}

@app.post("/peliculas/restaurar/{id}", tags=["Peliculas"])
def restaurar_pelicula(id: int, session: Session = SessionDep):
    db_pelicula = session.get(Pelicula, id)
    if not db_pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    db_pelicula.estado = True
    session.add(db_pelicula)
    session.commit()
    return {"mensaje": "Película restaurada"}

@app.get("/peliculas/historico", tags=["Peliculas"])
def peliculas_eliminadas(session: Session = SessionDep):
    statement = select(Pelicula).where(Pelicula.estado == False)
    return session.exec(statement).all()

# ----- CRUD Personajes -----
@app.get("/personajes", tags=["Personajes"])
def obtener_personajes(activos: bool = True, session: Session = SessionDep):
    statement = select(Personaje).where(Personaje.estado == activos)
    return session.exec(statement).all()

@app.post("/personajes", tags=["Personajes"])
def crear_personaje(personaje: Personaje, session: Session = SessionDep):
    session.add(personaje)
    session.commit()
    session.refresh(personaje)
    return personaje

@app.put("/personajes/{nombre}", tags=["Personajes"])
def actualizar_personaje(nombre: str, personaje: Personaje, session: Session = SessionDep):
    db_personaje = session.get(Personaje, nombre)
    if not db_personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    for key, value in personaje.dict(exclude_unset=True).items():
        setattr(db_personaje, key, value)
    session.add(db_personaje)
    session.commit()
    session.refresh(db_personaje)
    return db_personaje

@app.delete("/personajes/{nombre}", tags=["Personajes"])
def eliminar_personaje(nombre: str, session: Session = SessionDep):
    db_personaje = session.get(Personaje, nombre)
    if not db_personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    db_personaje.estado = False
    session.add(db_personaje)
    session.commit()
    return {"mensaje": "Personaje eliminado (soft delete)"}

@app.post("/personajes/restaurar/{nombre}", tags=["Personajes"])
def restaurar_personaje(nombre: str, session: Session = SessionDep):
    db_personaje = session.get(Personaje, nombre)
    if not db_personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    db_personaje.estado = True
    session.add(db_personaje)
    session.commit()
    return {"mensaje": "Personaje restaurado"}

@app.get("/personajes/historico", tags=["Personajes"])
def personajes_eliminados(session: Session = SessionDep):
    statement = select(Personaje).where(Personaje.estado == False)
    return session.exec(statement).all()

@app.post("/peliculas/{pelicula_id}/personajes/{nombre}", tags=["Peliculas-Personajes"])
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

@app.delete("/peliculas/{pelicula_id}/personajes/{nombre}", tags=["Peliculas-Personajes"])
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

# ----- CRUD Directores -----
@app.get("/directores", tags=["Directores"])
def obtener_directores(activos: bool = True, session: Session = SessionDep):
    statement = select(Director).where(Director.estado == activos)
    return session.exec(statement).all()

@app.post("/directores", tags=["Directores"])
def crear_director(director: Director, session: Session = SessionDep):
    session.add(director)
    session.commit()
    session.refresh(director)
    return director

@app.put("/directores/{nombre}", tags=["Directores"])
def actualizar_director(nombre: str, director: Director, session: Session = SessionDep):
    db_director = session.get(Director, nombre)
    if not db_director:
        raise HTTPException(status_code=404, detail="Director no encontrado")
    for key, value in director.dict(exclude_unset=True).items():
        setattr(db_director, key, value)
    session.add(db_director)
    session.commit()
    session.refresh(db_director)
    return db_director

@app.delete("/directores/{nombre}", tags=["Directores"])
def eliminar_director(nombre: str, session: Session = SessionDep):
    db_director = session.get(Director, nombre)
    if not db_director:
        raise HTTPException(status_code=404, detail="Director no encontrado")
    db_director.estado = False
    session.add(db_director)
    session.commit()
    return {"mensaje": "Director eliminado (soft delete)"}

@app.post("/directores/restaurar/{nombre}", tags=["Directores"])
def restaurar_director(nombre: str, session: Session = SessionDep):
    db_director = session.get(Director, nombre)
    if not db_director:
        raise HTTPException(status_code=404, detail="Director no encontrado")
    db_director.estado = True
    session.add(db_director)
    session.commit()
    return {"mensaje": "Director restaurado"}

@app.get("/directores/historico", tags=["Directores"])
def directores_eliminados(session: Session = SessionDep):
    statement = select(Director).where(Director.estado == False)
    return session.exec(statement).all()

# ------------------- CRUD Curiosidades -------------------

@app.get("/curiosidades", tags=["Curiosidades"])
def obtener_curiosidades(activos: bool = True, session: Session = SessionDep):
    statement = select(Curiosidad).where(Curiosidad.estado == activos)
    return session.exec(statement).all()

@app.post("/curiosidades", tags=["Curiosidades"])
def crear_curiosidad(curiosidad: Curiosidad, session: Session = SessionDep):
    session.add(curiosidad)
    session.commit()
    session.refresh(curiosidad)
    return curiosidad

@app.put("/curiosidades/{pelicula_id}", tags=["Curiosidades"])
def actualizar_curiosidad(pelicula_id: int, curiosidad: Curiosidad, session: Session = SessionDep):
    db_curiosidad = session.get(Curiosidad, pelicula_id)
    if not db_curiosidad:
        raise HTTPException(status_code=404, detail="Curiosidad no encontrada")
    for key, value in curiosidad.dict(exclude_unset=True).items():
        setattr(db_curiosidad, key, value)
    session.add(db_curiosidad)
    session.commit()
    session.refresh(db_curiosidad)
    return db_curiosidad

@app.delete("/curiosidades/{pelicula_id}", tags=["Curiosidades"])
def eliminar_curiosidad(pelicula_id: int, session: Session = SessionDep):
    db_curiosidad = session.get(Curiosidad, pelicula_id)
    if not db_curiosidad:
        raise HTTPException(status_code=404, detail="Curiosidad no encontrada")
    db_curiosidad.estado = False
    session.add(db_curiosidad)
    session.commit()
    return {"mensaje": "Curiosidad eliminada (soft delete)"}

@app.post("/curiosidades/restaurar/{pelicula_id}", tags=["Curiosidades"])
def restaurar_curiosidad(pelicula_id: int, session: Session = SessionDep):
    db_curiosidad = session.get(Curiosidad, pelicula_id)
    if not db_curiosidad:
        raise HTTPException(status_code=404, detail="Curiosidad no encontrada")
    db_curiosidad.estado = True
    session.add(db_curiosidad)
    session.commit()
    return {"mensaje": "Curiosidad restaurada"}

@app.get("/curiosidades/historico", tags=["Curiosidades"])
def curiosidades_eliminadas(session: Session = SessionDep):
    statement = select(Curiosidad).where(Curiosidad.estado == False)
    return session.exec(statement).all()