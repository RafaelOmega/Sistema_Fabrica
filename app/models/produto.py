from sqlalchemy import Column, Integer, String, Float
from app.database.base import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), unique=True, nullable=False)
    descricao = Column(String(255), nullable=False)
    peso = Column(Float, nullable=False, default=0.0)
    custo = Column(Float, nullable=False, default=0.0)
