"""
Teste de INTEGRAÇÃO (SQLite real, sem mocks) para o cálculo de saldo
de estoque, agora lido do kardex (movimentos_estoque) em vez de somado
em tempo real de itens_entrada/itens_saida.

Diferença importante em relação à versão anterior deste arquivo: os
dados de teste são criados através de
EntradaService.salvar()/SaidaService.salvar() (não por inserção direta
de Entrada/ItemEntrada/Saida/ItemSaida via SQLAlchemy), porque é
exatamente esse fluxo — dentro da mesma transação do salvar() — que
agora popula o kardex. Inserir os itens "por fora" dos services não
geraria nenhum movimento de estoque, e o saldo apareceria sempre zero.

Cenário montado (igual ao original):
    Produto A: 100 de entrada em 05/09 + 50 de entrada em 15/09;
               30 de saída em 10/09.
    Produto B: 20 de entrada em 05/09; 20 de saída em 06/09 (saldo 0).
    Produto C: sem nenhum lançamento.

Isso permite validar:
    - a soma correta de entradas e saídas;
    - o filtro por data (uma entrada POSTERIOR à data de corte não
      deve entrar na conta);
    - o produto sem nenhum lançamento (saldo 0);
    - o filtro `ocultar_zerados`;
    - o requisito central do kardex: editar uma entrada já salva
      recalcula o saldo corrente em vez de só empilhar um novo
      movimento por cima do antigo.
"""
from contextlib import contextmanager
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.motivo_entrada import Motivo_Entrada
from app.models.produto import Produto
from app.services.entrada_service import EntradaService
from app.services.estoque_service import EstoqueService
from app.services.saida_service import SaidaService


@pytest.fixture
def cenario_estoque(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    @contextmanager
    def fake_session_scope():
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # Cada módulo que faz `from app.database.connection import
    # session_scope` no topo do arquivo precisa ser substituído no seu
    # PRÓPRIO namespace, não só no de origem (ver explicação em
    # tests/test_saida_service_integration.py). Com o kardex, isso
    # agora inclui também o repositório de movimentos de estoque.
    for alvo in (
        "app.database.connection.session_scope",
        "app.repositories.entrada_repository.session_scope",
        "app.repositories.saida_repository.session_scope",
        "app.repositories.estoque_repository.session_scope",
        "app.repositories.movimento_estoque_repository.session_scope",
    ):
        monkeypatch.setattr(alvo, fake_session_scope)

    with SessionLocal() as s:
        produto_a = Produto(
            codigo="1", descricao="Produto A", peso=1.0,
            custo=10.0, prod_acabado=True, mat_prima=False,
            controla_estoque=True,
        )
        produto_b = Produto(
            codigo="2", descricao="Produto B", peso=1.0,
            custo=5.0, prod_acabado=True, mat_prima=False,
            controla_estoque=True,
        )
        produto_sem_lancamento = Produto(
            codigo="3", descricao="Produto C (sem movimento)",
            peso=1.0, custo=7.0, prod_acabado=True, mat_prima=False,
            controla_estoque=True,
        )
        motivo = Motivo_Entrada(codigo="1", descricao="Compra")
        s.add_all([produto_a, produto_b, produto_sem_lancamento, motivo])
        s.commit()

        return {
            "produto_a_id": produto_a.id,
            "produto_b_id": produto_b.id,
            "produto_c_id": produto_sem_lancamento.id,
            "motivo_id": motivo.id,
        }


def _lancar_entrada(sequencia, data_entrada, motivo_id, itens, entrada_id=None):
    return EntradaService().salvar(
        sequencia=sequencia,
        data_entrada=data_entrada,
        motivo_id=motivo_id,
        itens_data=itens,
        entrada_id=entrada_id,
    )


def _lancar_saida(sequencia, data_saida, itens):
    return SaidaService().salvar(
        sequencia=sequencia,
        data_saida=data_saida,
        itens_data=itens,
    )


def _por_produto_id(linhas, produto_id):
    return next(
        (linha for linha in linhas if linha["produto_id"] == produto_id),
        None,
    )


def test_saldo_soma_entradas_e_saidas_ate_a_data(cenario_estoque):
    ctx = cenario_estoque

    _lancar_entrada("1", date(2026, 9, 5), ctx["motivo_id"], [
        {"produto_id": ctx["produto_a_id"], "unidade": "UN",
         "quantidade": 100, "custo": 10.0},
    ])
    _lancar_entrada("2", date(2026, 9, 15), ctx["motivo_id"], [
        {"produto_id": ctx["produto_a_id"], "unidade": "UN",
         "quantidade": 50, "custo": 10.0},
    ])
    _lancar_entrada("3", date(2026, 9, 5), ctx["motivo_id"], [
        {"produto_id": ctx["produto_b_id"], "unidade": "UN",
         "quantidade": 20, "custo": 5.0},
    ])
    _lancar_saida("1", date(2026, 9, 10), [
        {"produto_id": ctx["produto_a_id"], "quantidade": 30, "custo": 10.0},
    ])
    _lancar_saida("2", date(2026, 9, 6), [
        {"produto_id": ctx["produto_b_id"], "quantidade": 20, "custo": 5.0},
    ])

    linhas = EstoqueService().listar_saldo(
        data_limite=date(2026, 9, 30), ocultar_zerados=False
    )

    produto_a = _por_produto_id(linhas, ctx["produto_a_id"])
    assert produto_a["qtd_entradas"] == pytest.approx(150.0)
    assert produto_a["qtd_saidas"] == pytest.approx(30.0)
    assert produto_a["saldo"] == pytest.approx(120.0)
    assert produto_a["valor_total"] == pytest.approx(1200.0)


def test_filtro_de_data_exclui_lancamentos_futuros(cenario_estoque):
    """A entrada de 50 unidades em 15/09 não deve contar se o corte
    for 10/09."""
    ctx = cenario_estoque

    _lancar_entrada("1", date(2026, 9, 5), ctx["motivo_id"], [
        {"produto_id": ctx["produto_a_id"], "unidade": "UN",
         "quantidade": 100, "custo": 10.0},
    ])
    _lancar_entrada("2", date(2026, 9, 15), ctx["motivo_id"], [
        {"produto_id": ctx["produto_a_id"], "unidade": "UN",
         "quantidade": 50, "custo": 10.0},
    ])
    _lancar_saida("1", date(2026, 9, 10), [
        {"produto_id": ctx["produto_a_id"], "quantidade": 30, "custo": 10.0},
    ])

    linhas = EstoqueService().listar_saldo(
        data_limite=date(2026, 9, 10), ocultar_zerados=False
    )

    produto_a = _por_produto_id(linhas, ctx["produto_a_id"])
    assert produto_a["qtd_entradas"] == pytest.approx(100.0)
    assert produto_a["qtd_saidas"] == pytest.approx(30.0)
    assert produto_a["saldo"] == pytest.approx(70.0)


def test_produto_sem_lancamento_aparece_com_saldo_zero(cenario_estoque):
    ctx = cenario_estoque

    linhas = EstoqueService().listar_saldo(
        data_limite=date(2026, 9, 30), ocultar_zerados=False
    )

    produto_c = _por_produto_id(linhas, ctx["produto_c_id"])
    assert produto_c is not None
    assert produto_c["qtd_entradas"] == 0.0
    assert produto_c["qtd_saidas"] == 0.0
    assert produto_c["saldo"] == 0.0


def test_ocultar_zerados_remove_produtos_com_saldo_zero(cenario_estoque):
    ctx = cenario_estoque

    _lancar_entrada("1", date(2026, 9, 5), ctx["motivo_id"], [
        {"produto_id": ctx["produto_b_id"], "unidade": "UN",
         "quantidade": 20, "custo": 5.0},
    ])
    _lancar_saida("1", date(2026, 9, 6), [
        {"produto_id": ctx["produto_b_id"], "quantidade": 20, "custo": 5.0},
    ])

    linhas = EstoqueService().listar_saldo(
        data_limite=date(2026, 9, 30), ocultar_zerados=True
    )

    # Produto B (entrada 20, saída 20 -> saldo 0) e Produto C (sem
    # movimento) devem sumir da lista.
    assert _por_produto_id(linhas, ctx["produto_b_id"]) is None
    assert _por_produto_id(linhas, ctx["produto_c_id"]) is None


def test_edicao_de_entrada_recalcula_o_kardex(cenario_estoque):
    """Cobre o requisito central do kardex combinado com o usuário:
    editar uma entrada já salva tem que RECALCULAR o saldo corrente de
    todos os movimentos seguintes daquele produto, não empilhar um
    novo movimento por cima do antigo."""
    ctx = cenario_estoque

    entrada = _lancar_entrada("1", date(2026, 9, 5), ctx["motivo_id"], [
        {"produto_id": ctx["produto_a_id"], "unidade": "UN",
         "quantidade": 100, "custo": 10.0},
    ])

    _, itens_salvos = EntradaService().buscar_com_itens(entrada.id)

    # Edita a quantidade do item de 100 para 40.
    _lancar_entrada(
        "1", date(2026, 9, 5), ctx["motivo_id"],
        [{
            "id": itens_salvos[0]["id"],
            "produto_id": ctx["produto_a_id"],
            "unidade": "UN",
            "quantidade": 40,
            "custo": 10.0,
        }],
        entrada_id=entrada.id,
    )

    linhas = EstoqueService().listar_saldo(
        data_limite=date(2026, 9, 30), ocultar_zerados=False
    )
    produto_a = _por_produto_id(linhas, ctx["produto_a_id"])
    assert produto_a["saldo"] == pytest.approx(40.0)
    assert produto_a["valor_total"] == pytest.approx(400.0)


def test_exclusao_de_entrada_remove_o_movimento_do_kardex(cenario_estoque):
    ctx = cenario_estoque

    entrada = _lancar_entrada("1", date(2026, 9, 5), ctx["motivo_id"], [
        {"produto_id": ctx["produto_a_id"], "unidade": "UN",
         "quantidade": 100, "custo": 10.0},
    ])

    EntradaService().excluir(entrada.id)

    linhas = EstoqueService().listar_saldo(
        data_limite=date(2026, 9, 30), ocultar_zerados=False
    )
    produto_a = _por_produto_id(linhas, ctx["produto_a_id"])
    assert produto_a["saldo"] == pytest.approx(0.0)
