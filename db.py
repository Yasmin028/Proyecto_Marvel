from sqlmodel import SQLModel, create_engine, Session

# 🔹 Conexión directa a Clever Cloud PostgreSQL
DATABASE_URL = "postgresql://uey3jcxwelplh9gijfwb:53z3WjVAfYrajauStXZnw26jLM7QWC@bof3lxgufoam6xb5qdsc-postgresql.services.clever-cloud.com:50013/bof3lxgufoam6xb5qdsc"

# 🔹 Crear el engine con PostgreSQL
engine = create_engine(DATABASE_URL, echo=True)

# 🔹 Crear todas las tablas en la base de datos remota
def create_all_tables():
    SQLModel.metadata.create_all(engine)

# 🔹 Sesión para usar en los routers
def get_session():
    with Session(engine) as session:
        yield session