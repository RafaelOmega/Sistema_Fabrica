from app.database.connection import session_scope
from app.models.movimento_estoque import MovimentoEstoque
from app.models.produto import Produto


class EstoqueRepository:
    """Lê o saldo de estoque diretamente do kardex (movimentos_estoque)
    em vez de somar itens_entrada/itens_saida em tempo real a cada
    consulta. Cada produto que controla estoque aparece com o saldo,
    custo médio e valor total já calculados e gravados na última linha
    do kardex até `data_limite` — só precisa ler, não recalcular.
    """

    def listar_saldo(self, data_limite, ocultar_zerados=False):
        """
        Retorna uma lista de dicts, um por produto com
        controla_estoque=True:
            {
                "produto_id", "codigo", "descricao",
                "qtd_entradas", "qtd_saidas", "saldo",
                "custo", "valor_total",
            }

        `custo` é o custo médio ponderado móvel do kardex naquela
        data (não mais o custo cadastrado atual do produto), e
        `valor_total` = saldo_quantidade * custo_médio, ambos já
        gravados na última linha do kardex até `data_limite` — não
        precisam ser recalculados aqui, só lidos.
        """
        with session_scope() as session:
            produtos = (
                session.query(Produto)
                .filter(Produto.controla_estoque.is_(True))
                .order_by(Produto.descricao.asc())
                .all()
            )

            produto_ids = [produto.id for produto in produtos]
            movimentos = []
            if produto_ids:
                movimentos = (
                    session.query(MovimentoEstoque)
                    .filter(
                        MovimentoEstoque.produto_id.in_(produto_ids),
                        MovimentoEstoque.data_movimento <= data_limite,
                    )
                    .order_by(
                        MovimentoEstoque.produto_id.asc(),
                        MovimentoEstoque.data_movimento.asc(),
                        MovimentoEstoque.id.asc(),
                    )
                    .all()
                )

            # A consulta já vem ordenada por (produto, data, id), então
            # o último movimento de cada produto que passar pelo loop
            # é sempre o mais recente até data_limite — dá para pegar
            # o saldo corrente sem uma segunda consulta por produto.
            agregados = {}
            for mov in movimentos:
                agregado = agregados.setdefault(
                    mov.produto_id,
                    {"qtd_entradas": 0.0, "qtd_saidas": 0.0, "ultimo": None},
                )
                qtd = float(mov.quantidade)
                if qtd >= 0:
                    agregado["qtd_entradas"] += qtd
                else:
                    agregado["qtd_saidas"] += -qtd
                agregado["ultimo"] = mov

            linhas = []
            for produto in produtos:
                agregado = agregados.get(produto.id)

                if agregado is None:
                    # Produto controla estoque mas não tem nenhum
                    # movimento até a data — saldo zero, sem cair em
                    # KeyError.
                    qtd_entradas = 0.0
                    qtd_saidas = 0.0
                    saldo = 0.0
                    valor_total = 0.0
                    custo = float(produto.custo or 0)
                else:
                    qtd_entradas = agregado["qtd_entradas"]
                    qtd_saidas = agregado["qtd_saidas"]
                    ultimo = agregado["ultimo"]
                    saldo = float(ultimo.saldo_quantidade)
                    valor_total = float(ultimo.saldo_valor)
                    custo = float(ultimo.custo_medio)

                if ocultar_zerados and abs(saldo) < 1e-9:
                    continue

                linhas.append({
                    "produto_id": produto.id,
                    "codigo": produto.codigo,
                    "descricao": produto.descricao,
                    "qtd_entradas": qtd_entradas,
                    "qtd_saidas": qtd_saidas,
                    "saldo": saldo,
                    "custo": custo,
                    "valor_total": valor_total,
                })
            return linhas
