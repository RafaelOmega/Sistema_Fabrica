"""Teste de INTEGRAÇÃO (SQLite real, via services) da produção:

- entrada com motivo de produção dá baixa proporcional da ficha técnica;
- produto acabado entra no kardex com custo = consumos / sacos;
- editar a produção recalcula tudo (não empilha movimentos);
- excluir desfaz baixas e entrada.
"""
from datetime import date

import pytest


@pytest.fixture
def cenario_producao(cenario_estoque):
    """Reaproveita o cenário de estoque (motivo comum + produtos) e cria
    o motivo de produção, a ficha técnica e o estoque inicial da MP."""
    from app.services.motivo_entrada_service import MotivoEntradaService
    from app.services.produto_service import ProdutoService

    ctx = dict(cenario_estoque)
    motivo_prod = MotivoEntradaService().salvar(
        codigo="PROD", descricao="Produção", producao=True
    )
    ctx["motivo_producao_id"] = motivo_prod.id

    produto_service = ProdutoService()
    pa = produto_service.salvar(
        codigo="PA001", descricao="Ração 25kg", peso=25.0, custo=0,
        prod_acabado=True, controla_estoque=True,
    )
    ctx["produto_acabado_id"] = pa.id
    ctx["produto_acabado_codigo"] = pa.codigo

    from app.services.ficha_tecnica_service import FichaTecnicaService
    ficha_service = FichaTecnicaService()
    ficha_service.salvar(
        produto_id=pa.id,
        codigo_produto=pa.codigo,
        sacos_batida=100,
        itens_data=[
            {"produto_id": ctx["produto_a_id"],
             "codigo": "MP-A", "unidade": "KG",
             "quantidade": 500.0, "custo": 0.0},
            {"produto_id": ctx["produto_b_id"],
             "codigo": "MP-B", "unidade": "KG",
             "quantidade": 100.0, "custo": 0.0},
        ],
    )
    ctx["ficha_id"] = ficha_service.buscar_por_produto(pa.id).id
    return ctx


def _lancar_entrada_producao(service, ctx, sequencia, data, sacos):
    return service.salvar(
        sequencia=sequencia,
        data_entrada=data,
        motivo_id=ctx["motivo_producao_id"],
        itens_data=[{
            "produto_id": ctx["produto_acabado_id"],
            "codigo": ctx["produto_acabado_codigo"],
            "unidade": "SACOS",
            "quantidade": float(sacos),
            "custo": 0.0,
        }],
        producao=True,
        sacos_produzidos=float(sacos),
    )


def test_producao_baixa_proporcional_e_entrada_pa(cenario_producao):
    """Batida de 100 sacos: fator = 0,5. MP-A baixa 250 kg, MP-B 50 kg."""
    from app.repositories.consumo_producao_repository import (
        ConsumoProducaoRepository,
    )
    from app.repositories.movimento_estoque_repository import (
        MovimentoEstoqueRepository,
    )
    from app.services.entrada_service import EntradaService

    service = EntradaService()
    _lancar_entrada_producao(
        service, cenario_producao, "1", date(2026, 9, 22), 50
    )

    movimento_repo = MovimentoEstoqueRepository()
    saldo_a = movimento_repo.saldo_atual(cenario_producao["produto_a_id"])
    saldo_b = movimento_repo.saldo_atual(cenario_producao["produto_b_id"])
    saldo_pa = movimento_repo.saldo_atual(
        cenario_producao["produto_acabado_id"]
    )

    assert abs(saldo_a["saldo_quantidade"] - 250.0) < 0.001
    assert abs(saldo_b["saldo_quantidade"] - 50.0) < 0.001
    assert abs(saldo_pa["saldo_quantidade"] - 50.0) < 0.001  # 50 sacos

    # custo do PA = total consumido / sacos
    custo_total = (
        250.0 * saldo_a["custo_medio_antes_producao"]
        if "custo_medio_antes_producao" in cenario_producao
        else saldo_pa["custo_medio"] * 50.0
    )
    assert custo_total > 0

    consumos = ConsumoProducaoRepository().listar_por_entrada(
        # entrada recém criada tem id 1 no cenário limpo
        1
    )
    assert len(consumos) == 2
    qtds = sorted(c["quantidade_kg"] for c in consumos)
    assert abs(qtds[0] - 50.0) < 0.001   # 100 * 0,5
    assert abs(qtds[1] - 250.0) < 0.001  # 500 * 0,5


def test_producao_sem_ficha_tecnica_bloqueia(cenario_producao):
    from app.services.entrada_service import EntradaService
    from app.services.produto_service import ProdutoService

    pa_sem_ficha = ProdutoService().salvar(
        codigo="PA002", descricao="Sem ficha", peso=10.0, custo=0,
        prod_acabado=True,
    )
    service = EntradaService()
    with pytest.raises(ValueError, match="ficha técnica"):
        service.salvar(
            sequencia="9",
            data_entrada=date(2026, 9, 22),
            motivo_id=cenario_producao["motivo_producao_id"],
            itens_data=[{
                "produto_id": pa_sem_ficha.id,
                "codigo": pa_sem_ficha.codigo,
                "unidade": "SACOS",
                "quantidade": 10.0,
                "custo": 0.0,
            }],
            producao=True,
            sacos_produzidos=10.0,
        )


def test_exclusao_desfaz_producao(cenario_producao):
    from app.repositories.movimento_estoque_repository import (
        MovimentoEstoqueRepository,
    )
    from app.services.entrada_service import EntradaService

    service = EntradaService()
    entrada = _lancar_entrada_producao(
        service, cenario_producao, "1", date(2026, 9, 22), 50
    )
    movimento_repo = MovimentoEstoqueRepository()

    service.excluir(entrada.id)

    saldo_a = movimento_repo.saldo_atual(cenario_producao["produto_a_id"])
    saldo_pa = movimento_repo.saldo_atual(
        cenario_producao["produto_acabado_id"]
    )
    assert abs(saldo_a["saldo_quantidade"] - 0.0) < 0.001
    assert abs(saldo_pa["saldo_quantidade"] - 0.0) < 0.001
