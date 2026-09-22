from app.database.connection import session_scope
from app.models.movimento_estoque import (
    MovimentoEstoque,
    TIPOS_QUE_SOMAM,
)
from app.models.produto import Produto


class MovimentoEstoqueRepository:
    """Mantém o kardex sincronizado com itens_entrada/itens_saida.

    Cada item de Entrada/Saída tem no máximo UM movimento de kardex
    associado, localizado por (origem_tabela, origem_id). Os
    repositórios de Entrada/Saída chamam `registrar_ou_atualizar` /
    `excluir_por_origem` dentro da MESMA transação do salvar(), então
    o kardex nasce/muda junto com a nota — nunca fica dessincronizado.
    """

    def registrar_ou_atualizar(self, session, origem_tabela, origem_id,
                               produto_id, quantidade, custo_unitario,
                               data_movimento, tipo):
        """Cria ou atualiza o movimento ligado a (origem_tabela,
        origem_id) e recalcula o saldo corrente do(s) produto(s)
        afetado(s).

        Só gera/mantém movimento se o produto controla estoque
        (controla_estoque=True). Se o produto não controlar estoque
        (ou deixou de controlar), qualquer movimento antigo é
        removido e nenhum novo é criado — o item continua existindo
        normalmente em itens_entrada/itens_saida, só não entra no
        kardex.
        """
        produto = session.query(Produto).filter_by(id=produto_id).first()
        controla = bool(produto and produto.controla_estoque)

        existente = (
            session.query(MovimentoEstoque)
            .filter_by(origem_tabela=origem_tabela, origem_id=origem_id)
            .first()
        )
        produto_id_antigo = existente.produto_id if existente else None

        if not controla:
            if existente:
                session.delete(existente)
                session.flush()
                self.recalcular(session, produto_id_antigo)
            return

        quantidade_assinada = (
            abs(quantidade) if tipo in TIPOS_QUE_SOMAM else -abs(quantidade)
        )

        if existente:
            existente.produto_id = produto_id
            existente.data_movimento = data_movimento
            existente.tipo = tipo
            existente.quantidade = quantidade_assinada
            existente.custo_unitario = custo_unitario
        else:
            session.add(MovimentoEstoque(
                origem_tabela=origem_tabela,
                origem_id=origem_id,
                produto_id=produto_id,
                data_movimento=data_movimento,
                tipo=tipo,
                quantidade=quantidade_assinada,
                custo_unitario=custo_unitario,
                saldo_quantidade=0,
                saldo_valor=0,
                custo_medio=0,
            ))
        session.flush()

        self.recalcular(session, produto_id)
        if produto_id_antigo and produto_id_antigo != produto_id:
            # O item de origem trocou de produto na edição — o produto
            # antigo também precisa ter seu saldo recalculado (perdeu
            # um movimento).
            self.recalcular(session, produto_id_antigo)

    def excluir_por_origem(self, session, origem_tabela, origem_id):
        """Remove o movimento ligado a (origem_tabela, origem_id), se
        existir, e recalcula o saldo do produto afetado. Retorna o
        produto_id afetado, ou None se não havia movimento."""
        existente = (
            session.query(MovimentoEstoque)
            .filter_by(origem_tabela=origem_tabela, origem_id=origem_id)
            .first()
        )
        if not existente:
            return None

        produto_id = existente.produto_id
        session.delete(existente)
        session.flush()
        self.recalcular(session, produto_id)
        return produto_id

    def recalcular(self, session, produto_id):
        """Reconstrói saldo_quantidade/saldo_valor/custo_medio de
        TODOS os movimentos do produto, em ordem cronológica (data,
        depois id como desempate), usando custo médio ponderado
        móvel:

        - Entrada: soma a quantidade e o valor (qtd * custo do
          movimento) ao saldo; o custo médio muda.
        - Saída/consumo: subtrai a quantidade valorizada ao custo
          médio vigente NO MOMENTO da saída (não ao custo do
          movimento); o custo médio não muda numa saída.

        É chamado sempre que um movimento é criado, editado ou
        excluído — por isso o kardex está sempre consistente mesmo
        quando o usuário edita ou apaga uma Entrada/Saída antiga.
        """
        if produto_id is None:
            return

        movimentos = (
            session.query(MovimentoEstoque)
            .filter_by(produto_id=produto_id)
            .order_by(
                MovimentoEstoque.data_movimento.asc(),
                MovimentoEstoque.id.asc(),
            )
            .all()
        )

        saldo_qtd = 0.0
        saldo_valor = 0.0
        for mov in movimentos:
            qtd = float(mov.quantidade)
            if qtd >= 0:
                saldo_qtd += qtd
                saldo_valor += qtd * float(mov.custo_unitario)
            else:
                custo_medio_atual = (
                    saldo_valor / saldo_qtd if saldo_qtd > 1e-9 else 0.0
                )
                saldo_qtd += qtd  # qtd já é negativa
                saldo_valor += qtd * custo_medio_atual

            mov.saldo_quantidade = round(saldo_qtd, 3)
            mov.saldo_valor = round(saldo_valor, 2)
            mov.custo_medio = (
                round(saldo_valor / saldo_qtd, 4) if saldo_qtd > 1e-9 else 0.0
            )

        session.flush()

    def saldo_atual(self, produto_id):
        """Saldo corrente (última linha do kardex) de um produto, ou
        zero se não há movimentos. Abre sua própria sessão — use
        dentro de uma transação já aberta apenas via `recalcular`."""
        with session_scope() as session:
            ultimo = (
                session.query(MovimentoEstoque)
                .filter_by(produto_id=produto_id)
                .order_by(
                    MovimentoEstoque.data_movimento.desc(),
                    MovimentoEstoque.id.desc(),
                )
                .first()
            )
            if not ultimo:
                return {
                    "saldo_quantidade": 0.0,
                    "saldo_valor": 0.0,
                    "custo_medio": 0.0,
                }
            return {
                "saldo_quantidade": float(ultimo.saldo_quantidade),
                "saldo_valor": float(ultimo.saldo_valor),
                "custo_medio": float(ultimo.custo_medio),
            }
