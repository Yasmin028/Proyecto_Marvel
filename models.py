from typing import List
from sqlmodel import SQLModel, Field, Relationship

# 🎬 Director
class Director(SQLModel, table=True):
    nombre: str = Field(primary_key=True)
    estado: bool = Field(default=True)
    
    peliculas: List["Pelicula"] = Relationship(back_populates="director")


# 🦸‍♀️ Tabla intermedia para N:N Película–Personaje
class PeliculaPersonajeLink(SQLModel, table=True):
    pelicula_id: int = Field(foreign_key="pelicula.id", primary_key=True)
    personaje_nombre: str = Field(foreign_key="personaje.nombre", primary_key=True)


# 🎥 Película
class Pelicula(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    titulo: str
    año: int
    director_nombre: str = Field(foreign_key="director.nombre")
    estado: bool = Field(default=True)

    director: Director = Relationship(back_populates="peliculas")
    personajes: List["Personaje"] = Relationship(
        back_populates="peliculas",
        link_model=PeliculaPersonajeLink
    )
    curiosidad: "Curiosidad" = Relationship(
        back_populates="pelicula", 
        sa_relationship_kwargs={"uselist": False}
    )


# 🦸‍♀️ Personaje
class Personaje(SQLModel, table=True):
    nombre: str = Field(primary_key=True)
    poder: str
    estado: bool = Field(default=True)

    peliculas: List[Pelicula] = Relationship(
        back_populates="personajes",
        link_model=PeliculaPersonajeLink
    )


# 📝 Curiosidad
class Curiosidad(SQLModel, table=True):
    pelicula_id: int = Field(foreign_key="pelicula.id", primary_key=True)
    contenido: str
    estado: bool = Field(default=True)

    pelicula: Pelicula = Relationship(back_populates="curiosidad")
