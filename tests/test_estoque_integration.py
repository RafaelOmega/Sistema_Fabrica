"""
Teste de INTEGRAÇÃO (SQLite real, sem mocks) para o cálculo de saldo
de estoque (Entradas - Saídas por produto, até uma data).

Cenário montado:
    Produto A: 100 de entrada em 05/09 + 50 de entrada em 15/09;
               30 de saída em 10/09.
    Produto B: 20 de entrada em 05/09; 20 de saída em 06/09 (saldo 0).

Isso permite validar:
    - a soma correta de entradas e saídas;
    - o filtro por data (uma entrada POSTERIOR à data de corte não
      deve entrar na conta);
    - o produto sem nenhum lançamento (saldo 0, sem quebrar o outer
      join);
    - o filtro `ocultar_zerados`.
"""
from contextlib import contextmanager
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.entrada import Entrada, ItemEntrada
from app.models.motivo_entrada import Motivo_Entrada
from app.models.produto import Produto
from app.models.saida import Saida, ItemSaida
from app.services.estoque_service import EstoqueService


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

    # `estoque_repository.py` faz `from app.database.connection import
    # session_scope` no topo do módulo — precisa ser substituído no
    # namespace de quem usa, não só no de origem (ver explicação em
    # tests/test_saida_service_integration.py).
    monkeypatch.setattr(
        "app.database.connection.session_scope", fake_session_scope
    )
    monkeypatch.setattr(
        "app.repositories.estoque_repository.session_scope",
        fake_session_scope,
    )

    with SessionLocal() as s:
        produto_a = Produto(
            codigo="1", descricao="Produto A", peso=1.0,
            custo=10.0, prod_acabado=True, mat_prima=False,
        )
        produto_b = Produto(
            codigo="2", descricao="Produto B", peso=1.0,
            custo=5.0, prod_acabado=True, mat_prima=False,
        )
        produto_sem_lancamento = Produto(
            codigo="3", descricao="Produto C (sem movimento)",
            peso=1.0, custo=7.0, prod_acabado=True, mat_prima=False,
        )
        s.add_all([produto_a, produto_b, produto_sem_lancamento])
        s.flush()

        motivo = Motivo_Entrada(codigo="1", descricao="Compra")
        s.add(motivo)
        s.flush()

        entrada_1 = Entrada(
            sequencia="1", data_entrada=date(2026, 9, 5),
            motivo_entrada_id=motivo.id,
        )
        entrada_2 = Entrada(
            sequencia="2", data_entrada=date(2026, 9, 15),
            motivo_entrada_id=motivo.id,
        )
        entrada_3 = Entrada(
            sequencia="3", data_entrada=date(2026, 9, 5),
            motivo_entrada_id=motivo.id,
        )
        s.add_all([entrada_1, entrada_2, entrada_3])
        s.flush()

        s.add_all([
            ItemEntrada(
                entrada_id=entrada_1.id, produto_id=produto_a.id,
                unidade="UN", quantidade=100, custo=10.0,
            ),
            ItemEntrada(
                entrada_id=entrada_2.id, produto_id=produto_a.id,
                unidade="UN", quantidade=50, custo=10.0,
            ),
            ItemEntrada(
                entrada_id=entrada_3.id, produto_id=produto_b.id,
                unidade="UN", quantidade=20, custo=5.0,
            ),
        ])

        saida_1 = Saida(sequencia="1", data_saida=date(2026, 9, 10))
        saida_2 = Saida(sequencia="2", data_saida=date(2026, 9, 6))
        s.add_all([saida_1, saida_2])
        s.flush()

        s.add_all([
            ItemSaida(
                saida_id=saida_1.id, produto_id=produto_a.id,
                quantidade=30, custo=10.0,
            ),
            ItemSaida(
                saida_id=saida_2.id, produto_id=produto_b.id,
                quantidade=20, custo=5.0,
            ),
        ])
        s.commit()

        return {
            "produto_a_id": produto_a.id,
            "produto_b_id": produto_b.id,
            "produto_c_id": produto_sem_lancamento.id,
        }


def _por_produto_id(linhas, produto_id):
    return next(
        (linha for linha in linhas if linha["produto_id"] == produto_id),
        None,
    )


def test_saldo_soma_entradas_e_saidas_ate_a_data(cenario_estoque):
    ctx = cenario_estoque
    service = EstoqueService()

    linhas = service.listar_saldo(
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
    service = EstoqueService()

    linhas = service.listar_saldo(
        data_limite=date(2026, 9, 10), ocultar_zerados=False
    )

    produto_a = _por_produto_id(linhas, ctx["produto_a_id"])
    assert produto_a["qtd_entradas"] == pytest.approx(100.0)
    assert produto_a["qtd_saidas"] == pytest.approx(30.0)
    assert produto_a["saldo"] == pytest.approx(70.0)


def test_produto_sem_lancamento_aparece_com_saldo_zero(cenario_estoque):
    ctx = cenario_estoque
    service = EstoqueService()

    linhas = service.listar_saldo(
        data_limite=date(2026, 9, 30), ocultar_zerados=False
    )

    produto_c = _por_produto_id(linhas, ctx["produto_c_id"])
    assert produto_c is not None
    assert produto_c["qtd_entradas"] == 0.0
    assert produto_c["qtd_saidas"] == 0.0
    assert produto_c["saldo"] == 0.0


def test_ocultar_zerados_remove_produtos_com_saldo_zero(cenario_estoque):
    ctx = cenario_estoque
    service = EstoqueService()

    linhas = service.listar_saldo(
        data_limite=date(2026, 9, 30), ocultar_zerados=True
    )

    # Produto B (entrada 20, saída 20 -> saldo 0) e Produto C (sem
    # movimento) devem sumir da lista; só o Produto A permanece.
    assert _por_produto_id(linhas, ctx["produto_b_id"]) is None
    assert _por_produto_id(linhas, ctx["produto_c_id"]) is None
    assert _por_produto_id(linhas, ctx["produto_a_id"]) is not None
