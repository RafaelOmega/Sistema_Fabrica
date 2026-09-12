from sqlalchemy import Column, Integer, Numeric, String

from app.database.base import Base


class RegraProdutoEspecial(Base):
    """Regra de cálculo especial por código de produto.

    Substitui o antigo dicionário REGRAS_PRODUTOS_ESPECIAIS, que ficava
    fixo no código-fonte (app/services/entrada_service.py). Agora cada
    regra é uma linha nesta tabela: adicionar, editar ou remover uma
    regra não exige mais alterar código nem gerar um novo build/exe.

    Exemplo de uso (Milho vendido em sacos de 60kg): o custo digitado
    na entrada é dividido por `divisor_custo` para chegar ao custo por
    kg do produto.
    """

    __tablename__ = "regras_produtos_especiais"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_produto = Column(String(50), unique=True, nullable=False, index=True)
    descricao = Column(String(255), nullable=False)
    divisor_custo = Column(Numeric(12, 3), nullable=False)

    def __repr__(self):
        return (
            f"RegraProdutoEspecial(id={self.id}, "
            f"codigo_produto='{self.codigo_produto}', "
            f"divisor_custo={self.divisor_custo})"
        )
