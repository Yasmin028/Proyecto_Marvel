# ✅ **README — Marvel**

---

## 📌 **1. Descripción del Proyecto**
- Aplicación fullstack basada en FastAPI.
- Combina API REST + vistas HTML con Jinja2.
- Gestiona:
  - Películas
  - Personajes
  - Directores
  - Curiosidades
- Incluye:
  - Dashboard con estadísticas
  - Buscador global
  - Subida de imágenes
  - Relaciones entre entidades
- Base de datos: PostgreSQL (Clever Cloud).
- Despliegue: Render.

---

## 📌 **2. Tecnologías Utilizadas**
- FastAPI
- SQLModel
- SQLAlchemy
- Pydantic
- Jinja2
- Bulma CSS
- PostgreSQL
- Uvicorn
- Render

---

## 📌 **3. Estructura del Proyecto**
- `main.py` → Punto de entrada.
- `db.py` → Conexión y sesión de base de datos.
- `models/`:
  - `models.py` → Modelos SQLModel.
  - `schemas.py` → Schemas Pydantic.
- `routers/`:
  - `peliculas.py`
  - `personajes.py`
  - `directores.py`
  - `curiosidades.py`
  - `buscar.py`
  - `dashboard.py`
- `templates/` → HTML.
- `static/` → CSS, JS, imágenes.
- `requirements.txt`.

---

## 📌 **4. Instalación Local**
- Clonar repositorio.
- Crear entorno virtual.
- Instalar dependencias.
- Configurar variable `DATABASE_URL`.
- Ejecutar servidor.

---

## 📌 **5. Comandos Principales**
- Crear entorno virtual:
  - `python -m venv venv`
- Activar entorno:
  - Linux/Mac: `source venv/bin/activate`
- Instalar dependencias:
  - `pip install -r requirements.txt`
- Ejecutar servidor:
  - `fastapi dev`

---

## 📌 **6. Variables de Entorno**
- `DATABASE_URL` → postgresql://uey3jcxwelplh9gijfwb:53z3WjVAfYrajauStXZnw26jLM7QWC@bof3lxgufoam6xb5qdsc-postgresql.services.clever-cloud.com:50013/bof3lxgufoam6xb5qdsc.

---

## 📌 **7. Despliegue en Render**
- Build Command:
  - `pip install -r requirements.txt`
- Start Command:
  - `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Variables necesarias:
  - `DATABASE_URL`
- Recomendación:
  - Usar “Clear build cache & deploy” si el deploy se queda colgado.

---

## 📌 **8. Requirements.txt Recomendado**
- `fastapi`
- `uvicorn`
- `sqlmodel`
- `psycopg2-binary`
- `jinja2`
- `python-multipart`
- `python-dotenv`

---

## 📌 **9. Rutas HTML (Frontend)**
- `/` → Inicio.
- `/peliculas/page` → Películas.
- `/personajes/page` → Personajes.
- `/directores/page` → Directores.
- `/curiosidades/page` → Curiosidades.
- `/dashboard/page` → Dashboard.

---

## 📌 **10. Rutas API (Backend)**

### Películas
- `GET /peliculas`
- `POST /peliculas`
- `PUT /peliculas/{id}`
- `DELETE /peliculas/{id}`
- `POST /peliculas/restaurar/{id}`

### Personajes
- `GET /personajes`
- `POST /personajes`
- `PUT /personajes/{nombre}`
- `DELETE /personajes/{nombre}`
- `POST /personajes/restaurar/{nombre}`

### Directores
- CRUD Agregar y eliminar.

### Curiosidades
- CRUD Agregar y eliminar.

### Buscador
- `GET /buscar?q=texto`.

---

## 📌 **11. Funcionalidades Principales**
- CRUD para todas las entidades.
- Subida de imágenes con validación.
- Soft delete.
- Relaciones Películas ↔ Personajes.
- Dashboard con estadísticas.
- Buscador global.
- Arquitectura modular.
- Código limpio y mantenible.
- Totalmente portable y desplegable.

---

## 📌 **12. Gestión de Imágenes**
- Subida mediante `UploadFile`.
- Validación de tipo MIME.
- Guardado en `static/img/...`.
- Soporte para PNG, JPG, WEBP.
- Compatible con Render.

---

## 📌 **13. Dashboard**
- Películas por año.
- Personajes activos/inactivos.
- Películas por director.
- Gráficos dinámicos.
- Estadísticas en tiempo real.

---

## 📌 **14. Licencia**
- Uso personal y educativo.

---

Si quieres, puedo generarte **una versión con emojis más vistosos**, o **una versión minimalista**, o incluso **una versión con capturas de pantalla**.
