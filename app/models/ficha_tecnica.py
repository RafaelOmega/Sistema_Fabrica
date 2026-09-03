from sqlalchemy import Column, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.base import Base


class FichaTecnica(Base):
    """Ficha técnica de um produto acabado: define a composição
    (matérias-primas e quantidades) necessárias para produzi-lo,
    além da quantidade de sacos gerados por batida."""

    __tablename__ = "fichas_tecnicas"
    __table_args__ = (
        UniqueConstraint(
            "produto_acabado_id", name="uq_ficha_tecnica_produto_acabado"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    produto_acabado_id = Column(
        Integer, ForeignKey("produtos.id"), nullable=False, index=True
    )
    sacos_por_batida = Column(Integer, nullable=False, default=0)

    produto_acabado = relationship("Produto", foreign_keys=[produto_acabado_id])
    itens = relationship(
        "ItemFichaTecnica", back_populates="ficha_tecnica",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"FichaTecnica(id={self.id}, "
            f"produto_acabado_id={self.produto_acabado_id}, "
            f"sacos_por_batida={self.sacos_por_batida})"
        )


class ItemFichaTecnica(Base):
    __tablename__ = "itens_ficha_tecnica"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ficha_tecnica_id = Column(
        Integer, ForeignKey("fichas_tecnicas.id"), nullable=False, index=True
    )
    materia_prima_id = Column(
        Integer, ForeignKey("produtos.id"), nullable=False
    )
    quantidade = Column(Numeric(12, 3), nullable=False)

    ficha_tecnica = relationship("FichaTecnica", back_populates="itens")
    materia_prima = relationship("Produto", foreign_keys=[materia_prima_id])

    def __repr__(self):
        return (
            f"ItemFichaTecnica(id={self.id}, "
            f"ficha_tecnica_id={self.ficha_tecnica_id}, "
            f"materia_prima_id={self.materia_prima_id}, "
            f"quantidade={self.quantidade})"
        )
