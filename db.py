import os
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://uhyxf2cbb08u4dxfwwln:PKjyZfNzAUIfQTws2InjYP5pylErtr@bhxiwqkwcuwbckhtwevk-postgresql.services.clever-cloud.com:50013/bhxiwqkwcuwbckhtwevk"
)

# ✅ pool_pre_ping evita conexiones muertas (soluciona tu error)
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

def create_all_tables(engine):
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session