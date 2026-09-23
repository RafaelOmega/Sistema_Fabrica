from app.database.base import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import relationship


class FichaTecnica(Base):
    __tablename__ = "fichas_tecnicas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    codigo_produto = Column(String(50), nullable=False)  # ← ADICIONADO
    sacos_batida = Column(Numeric(12, 4), nullable=False, default=0)

    itens = relationship(
        "ItemFichaTecnica",
        back_populates="ficha",
        cascade="all, delete-orphan",
        order_by="ItemFichaTecnica.id",
    )


class ItemFichaTecnica(Base):
    __tablename__ = "itens_ficha_tecnica"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ficha_id = Column(
        Integer, ForeignKey("fichas_tecnicas.id"), nullable=False
    )
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    codigo_produto = Column(String(50), nullable=False)  # ← ADICIONADO
    quantidade_kg = Column(Numeric(12, 3), nullable=False, default=0)

    ficha = relationship("FichaTecnica", back_populates="itens")
