from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, func

from app.database.base import Base

# Tipos de movimento. CONSUMO_PRODUCAO fica reservado para quando a
# baixa automática de matéria-prima na Produção for implementada — já
# nasce previsto aqui para não exigir migração de schema depois.
TIPO_ENTRADA = "ENTRADA"
TIPO_SAIDA = "SAIDA"
TIPO_CONSUMO_PRODUCAO = "CONSUMO_PRODUCAO"
TIPO_AJUSTE = "AJUSTE"

# Usados para decidir o sinal da quantidade gravada.
TIPOS_QUE_SOMAM = {TIPO_ENTRADA}
TIPOS_QUE_SUBTRAEM = {TIPO_SAIDA, TIPO_CONSUMO_PRODUCAO}


class MovimentoEstoque(Base):
    """Kardex: um registro por movimento de estoque, com o saldo
    corrente do produto já calculado e gravado na própria linha
    (saldo_quantidade, saldo_valor, custo_medio), usando custo médio
    ponderado móvel.

    Não substitui itens_entrada/itens_saida (que continuam sendo o
    detalhe de cada nota) — é alimentado a partir deles pelos
    repositórios de Entrada/Saída, na MESMA transação do salvar(), e
    passa a ser a fonte de verdade para o relatório de Estoque
    (EstoqueRepository.listar_saldo).

    origem_tabela + origem_id apontam para a linha que gerou este
    movimento (ex.: "itens_entrada" + id do ItemEntrada). É por aí que
    o movimento é localizado para ser atualizado ou excluído quando o
    item de origem é editado/excluído — e por isso o kardex fica
    sempre consistente com edição/exclusão de Entradas e Saídas
    (ver MovimentoEstoqueRepository.recalcular).
    """

    __tablename__ = "movimentos_estoque"

    id = Column(Integer, primary_key=True, autoincrement=True)
    produto_id = Column(
        Integer, ForeignKey("produtos.id"), nullable=False, index=True
    )
    data_movimento = Column(Date, nullable=False, index=True)
    tipo = Column(String(20), nullable=False)

    # Quantidade ASSINADA: positiva para entrada, negativa para
    # saída/consumo. Simplifica o cálculo cumulativo em recalcular().
    quantidade = Column(Numeric(12, 3), nullable=False)
    custo_unitario = Column(Numeric(12, 2), nullable=False, default=0)

    # Saldo corrente logo APÓS este movimento. Recalculado sempre que
    # qualquer movimento do mesmo produto é criado, editado ou
    # excluído — nunca fica "desatualizado".
    saldo_quantidade = Column(Numeric(12, 3), nullable=False, default=0)
    saldo_valor = Column(Numeric(14, 2), nullable=False, default=0)
    custo_medio = Column(Numeric(12, 4), nullable=False, default=0)

    origem_tabela = Column(String(30), nullable=False, index=True)
    origem_id = Column(Integer, nullable=False, index=True)

    criado_em = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return (
            f"MovimentoEstoque(id={self.id}, produto_id={self.produto_id}, "
            f"tipo='{self.tipo}', quantidade={self.quantidade}, "
            f"saldo_quantidade={self.saldo_quantidade})"
        )
