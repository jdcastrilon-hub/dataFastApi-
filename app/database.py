from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#usuario:password@localhost:5432/nombre_db
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123456@localhost:5432/Data_BD"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para inyectar la sesión en los endpoints (Como el EntityManager)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()