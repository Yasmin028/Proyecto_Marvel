from pydantic import BaseModel, Field, validator
from typing import Optional

class PeliculaCreate(BaseModel):
    titulo: str = Field(..., min_length=2, max_length=100)
    año: int = Field(..., ge=1900, le=2025)
    imagen_url: Optional[str] = None   # <- nuevo campo

    @validator("titulo")
    def titulo_no_vacio(cls, v):
        if not v.strip():
            raise ValueError("El título no puede estar vacío")
        return v

class PersonajeCreate(BaseModel):
    nombre: str = Field(..., min_length=2)
    poder: str = Field(..., min_length=2)
    imagen_url: Optional[str] = None

from pydantic import BaseModel, Field, validator
from typing import Optional

class PeliculaCreate(BaseModel):
    titulo: str = Field(..., min_length=2, max_length=100)
    año: int = Field(..., ge=1900, le=2025)
    imagen_url: Optional[str] = None   # <- nuevo campo

    @validator("titulo")
    def titulo_no_vacio(cls, v):
        if not v.strip():
            raise ValueError("El título no puede estar vacío")
        return v

class PersonajeCreate(BaseModel):
    nombre: str = Field(..., min_length=2)
    poder: str = Field(..., min_length=2)
    imagen_url: Optional[str] = None

class DirectorCreate(BaseModel):
    nombre: str = Field(..., min_length=2)
    biografia: Optional[str] = None
    imagen_url: Optional[str] = None
    estado: Optional[bool] = True

class CuriosidadCreate(BaseModel):
    pelicula_id: int = Field(..., ge=1)
    contenido: str = Field(..., min_length=5)
    estado: Optional[bool] = True 

class CuriosidadCreate(BaseModel):
    pelicula_id: int = Field(..., ge=1)
    contenido: str = Field(..., min_length=5)
    estado: Optional[bool] = True 