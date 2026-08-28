from sqlalchemy import Column, Float, Integer, Numeric, String

from app.database.base import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    descricao = Column(String(255), nullable=False, index=True)
    peso = Column(Float, nullable=False, default=0.0)
    custo = Column(Numeric(10, 2), nullable=False, default=0)

    def __repr__(self):
        return (
            f"Produto(id={self.id}, codigo='{self.codigo}', "
            f"descricao='{self.descricao}', peso={self.peso}, custo={self.custo})"
        )
