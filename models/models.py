from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class Director(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True)   # 👈 ahora PostgreSQL lo acepta
    imagen_url: str | None = None
    estado: bool
    biografia: str | None = None
    # Relación con Películas
    peliculas: List["Pelicula"] = Relationship(back_populates="director")


class PeliculaPersonajeLink(SQLModel, table=True):
    pelicula_id: int = Field(foreign_key="pelicula.id", primary_key=True)
    personaje_nombre: str = Field(foreign_key="personaje.nombre", primary_key=True)


class Pelicula(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    titulo: str
    año: int
    director_nombre: str = Field(foreign_key="director.nombre")  # 👈 sigue igual
    estado: bool
    imagen_url: str | None = None

    # Relaciones (solo una vez cada una)
    director: Optional[Director] = Relationship(back_populates="peliculas")
    personajes: List["Personaje"] = Relationship(
        back_populates="peliculas",
        link_model=PeliculaPersonajeLink
    )
    curiosidad: Optional["Curiosidad"] = Relationship(
        back_populates="pelicula",
        sa_relationship_kwargs={"uselist": False}
    )


class Personaje(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre: str
    poder: str | None = None
    estado: bool = True
    imagen_url: str | None = None

    peliculas: List[Pelicula] = Relationship(
        back_populates="personajes",
        link_model=PeliculaPersonajeLink
    )


class Curiosidad(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    pelicula_id: int = Field(foreign_key="pelicula.id")
    contenido: str
    estado: bool = True

    pelicula: Pelicula = Relationship(back_populates="curiosidad")