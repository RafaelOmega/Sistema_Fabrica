from app.database.connection import session_scope
from app.models.consumo_producao import ConsumoProducao
from app.models.movimento_estoque import TIPO_CONSUMO_PRODUCAO
from app.repositories.movimento_estoque_repository import (
    MovimentoEstoqueRepository,
)


class ConsumoProducaoRepository:
    """Baixas de matéria-prima por produção + sincronização do kardex.

    Cada consumo tem no máximo UM movimento de kardex, localizado por
    (origem_tabela='consumos_producao', origem_id). Tudo é chamado
    dentro da MESMA transação do salvar() da entrada — o kardex nasce
    ou mora junto com a nota.
    """

    def __init__(self):
        self.movimento_repo = MovimentoEstoqueRepository()

    def listar_por_entrada(self, entrada_id):
        """Consumos de uma entrada (dicts com dados do produto)."""
        from app.models.produto import Produto

        with session_scope() as session:
            resultados = (
                session.query(ConsumoProducao, Produto.codigo,
                              Produto.descricao)
                .join(Produto, ConsumoProducao.produto_id == Produto.id)
                .filter(ConsumoProducao.entrada_id == entrada_id)
                .order_by(ConsumoProducao.id.asc())
                .all()
            )
            consumos = []
            for consumo, codigo, descricao in resultados:
                consumos.append({
                    "id": consumo.id,
                    "entrada_id": consumo.entrada_id,
                    "produto_id": consumo.produto_id,
                    "codigo": codigo,
                    "descricao": descricao,
                    "quantidade_kg": float(consumo.quantidade_kg),
                    "custo_unitario": float(consumo.custo_unitario),
                })
            return consumos

    def criar_com_movimento(self, session, entrada_id, produto_id,
                            quantidade_kg, custo_unitario, data_producao):
        """Cria o consumo e o movimento de kardex (CONSUMO_PRODUCAO,
        quantidade negativa) na sessão compartilhada. Só gera movimento
        se o produto controla estoque (decisão do movimento_repo)."""
        consumo = ConsumoProducao(
            entrada_id=entrada_id,
            produto_id=produto_id,
            quantidade_kg=quantidade_kg,
            custo_unitario=custo_unitario,
        )
        session.add(consumo)
        session.flush()  # garante consumo.id para a origem do kardex

        self.movimento_repo.registrar_ou_atualizar(
            session,
            origem_tabela="consumos_producao",
            origem_id=consumo.id,
            produto_id=produto_id,
            quantidade=-float(quantidade_kg),
            custo_unitario=float(custo_unitario),
            data_movimento=data_producao,
            tipo=TIPO_CONSUMO_PRODUCAO,
        )
        return consumo

    def excluir_por_entrada(self, session, entrada_id):
        """Remove todos os consumos da entrada e seus movimentos de
        kardex — ANTES do cascade apagar a entrada. Usado na edição
        (recria depois) e na exclusão (só remove)."""
        consumos = (
            session.query(ConsumoProducao)
            .filter_by(entrada_id=entrada_id)
            .all()
        )
        for consumo in consumos:
            self.movimento_repo.excluir_por_origem(
                session, "consumos_producao", consumo.id
            )
            session.delete(consumo)
