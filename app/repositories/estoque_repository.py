from sqlalchemy import func

from app.database.connection import session_scope
from app.models.entrada import Entrada, ItemEntrada
from app.models.produto import Produto
from app.models.saida import Saida, ItemSaida


class EstoqueRepository:
    def listar_saldo(self, data_limite, ocultar_zerados=False):
        """
        Calcula, para cada produto, o saldo em estoque até `data_limite`
        (inclusive): soma de quantidades entradas menos soma de
        quantidades saídas, ambas filtradas pela data do lançamento.

        Retorna uma lista de dicts, um por produto:
            {
                "produto_id", "codigo", "descricao",
                "qtd_entradas", "qtd_saidas", "saldo",
                "custo", "valor_total",
            }

        `custo` é o custo cadastrado ATUAL do produto (não um custo
        médio histórico) e `valor_total` = saldo * custo. Isso é uma
        aproximação — o sistema não mantém custo médio ponderado por
        lançamento, só o custo "corrente" do produto (o mesmo usado em
        Entrada/Ficha Técnica).
        """
        with session_scope() as session:
            entradas_sub = (
                session.query(
                    ItemEntrada.produto_id.label("produto_id"),
                    func.sum(ItemEntrada.quantidade).label(
                        "qtd_entradas"
                    ),
                )
                .join(Entrada, Entrada.id == ItemEntrada.entrada_id)
                .filter(Entrada.data_entrada <= data_limite)
                .group_by(ItemEntrada.produto_id)
                .subquery()
            )

            saidas_sub = (
                session.query(
                    ItemSaida.produto_id.label("produto_id"),
                    func.sum(ItemSaida.quantidade).label("qtd_saidas"),
                )
                .join(Saida, Saida.id == ItemSaida.saida_id)
                .filter(Saida.data_saida <= data_limite)
                .group_by(ItemSaida.produto_id)
                .subquery()
            )

            resultados = (
                session.query(
                    Produto.id,
                    Produto.codigo,
                    Produto.descricao,
                    Produto.custo,
                    entradas_sub.c.qtd_entradas,
                    saidas_sub.c.qtd_saidas,
                )
                .outerjoin(
                    entradas_sub,
                    entradas_sub.c.produto_id == Produto.id,
                )
                .outerjoin(
                    saidas_sub,
                    saidas_sub.c.produto_id == Produto.id,
                )
                .order_by(Produto.descricao.asc())
                .all()
            )

            linhas = []
            for (produto_id, codigo, descricao, custo,
                 qtd_entradas, qtd_saidas) in resultados:
                qtd_entradas = (
                    float(qtd_entradas) if qtd_entradas else 0.0
                )
                qtd_saidas = float(qtd_saidas) if qtd_saidas else 0.0
                saldo = qtd_entradas - qtd_saidas

                if ocultar_zerados and abs(saldo) < 1e-9:
                    continue

                custo_f = float(custo) if custo else 0.0
                linhas.append({
                    "produto_id": produto_id,
                    "codigo": codigo,
                    "descricao": descricao,
                    "qtd_entradas": qtd_entradas,
                    "qtd_saidas": qtd_saidas,
                    "saldo": saldo,
                    "custo": custo_f,
                    "valor_total": saldo * custo_f,
                })
            return linhas
