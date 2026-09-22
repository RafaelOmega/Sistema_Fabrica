from sqlalchemy import Column, ForeignKey, Integer, Numeric

from app.database.base import Base


class ConsumoProducao(Base):
    """Baixa de matéria-prima gerada por uma produção (entrada com motivo
    de produção).

    Um registro por item da ficha técnica escalado pelo fator de
    proporção da batida. Serve de ORIGEM para o movimento de kardex
    (origem_tabela='consumos_producao') — os itens da ficha técnica não
    podem ser origem, porque são reutilizados em toda batida.
    """
    __tablename__ = "consumos_producao"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entrada_id = Column(Integer, ForeignKey("entradas.id"),
                        nullable=False, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"),
                        nullable=False, index=True)
    quantidade_kg = Column(Numeric(12, 3), nullable=False)
    custo_unitario = Column(Numeric(12, 4), nullable=False)

    def __repr__(self):
        return (
            f"ConsumoProducao(id={self.id}, entrada_id={self.entrada_id}, "
            f"produto_id={self.produto_id}, "
            f"quantidade_kg={self.quantidade_kg}, "
            f"custo_unitario={self.custo_unitario})"
        )
