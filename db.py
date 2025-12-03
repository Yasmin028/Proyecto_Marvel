from sqlmodel import SQLModel, create_engine, Session

# 🔹 Conexión directa a Clever Cloud PostgreSQL
DATABASE_URL = "postgresql://ujog1zhqq66a2owfkdrx:D6iMD2PVrNczXercD8MmCceoz9rAuK@bkc3nx8y391ucsddnqam-postgresql.services.clever-cloud.com:50013/bkc3nx8y391ucsddnqam"

# 🔹 Crear el engine con PostgreSQL
engine = create_engine(DATABASE_URL, echo=True)

# 🔹 Crear todas las tablas en la base de datos remota
def create_all_tables():
    SQLModel.metadata.create_all(engine)

# 🔹 Sesión para usar en los routers
def get_session():
    with Session(engine) as session:
        yield session