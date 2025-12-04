from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class Director(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True)   # 👈 único para evitar duplicados
    imagen_url: Optional[str] = None
    imagen_data: Optional[bytes] = None            # 👈 campo binario
    estado: bool = True
    biografia: Optional[str] = None

    # Relación con Películas
    peliculas: List["Pelicula"] = Relationship(back_populates="director")


class PeliculaPersonajeLink(SQLModel, table=True):
    pelicula_id: int = Field(foreign_key="pelicula.id", primary_key=True)
    personaje_id: int = Field(foreign_key="personaje.id", primary_key=True)  # 👈 ahora referencia id


class Pelicula(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    año: Optional[int] = None
    estado: bool = True
    imagen_url: Optional[str] = None
    imagen_data: Optional[bytes] = None
    
    # 🔹 Clave foránea que faltaba
    director_id: Optional[int] = Field(default=None, foreign_key="director.id")

    # Relaciones
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
    id: Optional[int] = Field(default=None, primary_key=True)   # 👈 clave primaria
    nombre: str = Field(index=True, unique=True)                # 👈 único
    poder: Optional[str] = None
    estado: bool = True
    imagen_url: Optional[str] = None
    imagen_data: Optional[bytes] = None

    peliculas: List[Pelicula] = Relationship(
        back_populates="personajes",
        link_model=PeliculaPersonajeLink
    )


class Curiosidad(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pelicula_id: int = Field(foreign_key="pelicula.id")
    contenido: str
    estado: bool = True

    pelicula: Pelicula = Relationship(back_populates="curiosidad")