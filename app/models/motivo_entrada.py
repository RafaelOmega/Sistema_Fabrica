from sqlalchemy import Boolean, Column, Integer, String

from app.database.base import Base


class Motivo_Entrada(Base):
    __tablename__ = "motivos_entrada"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    descricao = Column(String(255), nullable=False, index=True)
    producao = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return (
            f"Motivo_Entrada(id={self.id}, codigo='{self.codigo}', "
            f"descricao='{self.descricao}', producao={self.producao})"
        )
