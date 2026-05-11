import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import uuid
from datetime import datetime

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TransacaoDB(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    banco = Column(String, index=True)
    data_transacao = Column(String)
    tipo = Column(String)
    valor = Column(Float)
    estabelecimento = Column(String)
    criado_em = Column(DateTime, default=datetime.utcnow)

def criar_tabelas():
    try:
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso no PostgreSQL!")
    except Exception as e:
        print(f"Erro ao conectar no banco: {e}")

if __name__ == "__main__":
    criar_tabelas()