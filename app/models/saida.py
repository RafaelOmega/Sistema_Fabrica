from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base import Base


class Saida(Base):
    __tablename__ = "saidas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sequencia = Column(String(50), unique=True, nullable=False, index=True)
    data_saida = Column(Date, nullable=False)

    itens = relationship(
        "ItemSaida", back_populates="saida",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"Saida(id={self.id}, sequencia='{self.sequencia}', "
            f"data='{self.data_saida}')"
        )


class ItemSaida(Base):
    __tablename__ = "itens_saida"

    id = Column(Integer, primary_key=True, autoincrement=True)
    saida_id = Column(
        Integer, ForeignKey("saidas.id"), nullable=False, index=True
    )
    produto_id = Column(
        Integer, ForeignKey("produtos.id"), nullable=False
    )
    quantidade = Column(Numeric(12, 3), nullable=False)
    custo = Column(Numeric(12, 2), nullable=False)

    saida = relationship("Saida", back_populates="itens")
    produto = relationship("Produto")
