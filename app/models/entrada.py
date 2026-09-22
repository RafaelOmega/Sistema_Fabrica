from sqlalchemy import (
    Column, Integer, String, Numeric, Date, ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class Entrada(Base):
    __tablename__ = "entradas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sequencia = Column(String(50), unique=True, nullable=False, index=True)
    data_entrada = Column(Date, nullable=False)
    motivo_entrada_id = Column(
        Integer, ForeignKey("motivos_entrada.id"), nullable=False
    )

    itens = relationship(
        "ItemEntrada", back_populates="entrada",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"Entrada(id={self.id}, sequencia='{self.sequencia}', "
            f"data='{self.data_entrada}')"
        )


class ItemEntrada(Base):
    __tablename__ = "itens_entrada"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entrada_id = Column(
        Integer, ForeignKey("entradas.id"), nullable=False, index=True
    )
    produto_id = Column(
        Integer, ForeignKey("produtos.id"), nullable=False
    )
    unidade = Column(String(10), nullable=False)
    quantidade = Column(Numeric(12, 3), nullable=False)
    custo = Column(Numeric(12, 4), nullable=False)

    entrada = relationship("Entrada", back_populates="itens")
    produto = relationship("Produto")
