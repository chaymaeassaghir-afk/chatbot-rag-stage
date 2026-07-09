from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import *

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base est définie ici
Base = declarative_base()

try:
    with engine.connect():
        print("Connexion PostgreSQL réussie !")
except Exception as e:
    print("Erreur :", e)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()