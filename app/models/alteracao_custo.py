from datetime import date

from sqlalchemy import Column, Date, Float, Integer, String

from app.database.base import Base


class AlteracaoCusto(Base):
    __tablename__ = "tb_Alteracao_Custo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data_alteracao = Column(Date, nullable=False, default=date.today)
    codigo_produto = Column(String(50), nullable=False)
    custo_anterior = Column(Float, nullable=False)
    custo_atual = Column(Float, nullable=False)
