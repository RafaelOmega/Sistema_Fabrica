from sqlalchemy import Boolean, Column, Float, Integer, Numeric, String

from app.database.base import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    descricao = Column(String(255), nullable=False, index=True)
    peso = Column(Numeric(12, 4), nullable=False, default=0)
    custo = Column(Numeric(12, 4), nullable=False, default=0)
    prod_acabado = Column(Boolean, nullable=False, default=False)
    mat_prima = Column(Boolean, nullable=False, default=False)
    mao_obra = Column(Boolean, nullable=False, default=False)
    controla_estoque = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return (
            f"Produto(id={self.id}, codigo='{self.codigo}', "
            f"descricao='{self.descricao}', peso={self.peso}, custo={self.custo}, "
            f"prod_acabado={self.prod_acabado}, mat_prima={self.mat_prima}, "
            f"mao_obra={self.mao_obra}, controla_estoque={self.controla_estoque})"
        )
