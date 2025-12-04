import os
from sqlmodel import SQLModel, Session, create_engine

# ✅ 1. URL de la base de datos (local o Clever Cloud)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://uey3jcxwelplh9gijfwb:53z3WjVAfYrajauStXZnw26jLM7QWC@bof3lxgufoam6xb5qdsc-postgresql.services.clever-cloud.com:50013/bof3lxgufoam6xb5qdsc"
)

# ✅ 2. Crear engine global (para usarlo en toda la app)
engine = create_engine(DATABASE_URL, echo=False)

# ✅ 3. Función para crear todas las tablas
def create_all_tables(engine):
    SQLModel.metadata.create_all(engine)

# ✅ 4. Sesión para usar en los routers (SIN parámetros)
def get_session():
    with Session(engine) as session:
        yield session