"""
Teste de INTEGRAÇÃO (SQLite real, sem mocks) para SaidaService.salvar().

Ver tests/test_entrada_service_integration.py para a explicação
completa de por que esse teste existe separado dos testes com
MagicMock: aqui garantimos que SaidaRepository (escrito já com o
padrão correto de expunge condicional) de fato não repete o bug de
sessão encontrado em produção no módulo de Entrada.
"""
from contextlib import contextmanager
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.produto import Produto
from app.services.saida_service import SaidaService


@pytest.fixture
def banco_sqlite_em_memoria(monkeypatch):
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

    monkeypatch.setattr(
        "app.database.connection.session_scope", fake_session_scope
    )
    # `saida_repository.py` faz `from app.database.connection import
    # session_scope` no topo do arquivo (import de módulo, não local
    # dentro de função como em SaidaService.salvar()). Esse nome já
    # fica vinculado à função original na primeira importação do
    # módulo, então também precisa ser substituído diretamente onde é
    # usado — só faz efeito lá.
    monkeypatch.setattr(
        "app.repositories.saida_repository.session_scope",
        fake_session_scope,
    )

    with SessionLocal() as setup_session:
        produto = Produto(
            codigo="9999",
            descricao="Ração Pronta 25KG",
            peso=25.0,
            custo=2.50,
            prod_acabado=True,
            mat_prima=False,
        )
        setup_session.add(produto)
        setup_session.commit()
        setup_session.refresh(produto)
        produto_id = produto.id

    return {"produto_id": produto_id}


def test_salvar_saida_com_itens_nao_quebra_a_sessao(
    banco_sqlite_em_memoria,
):
    ctx = banco_sqlite_em_memoria
    service = SaidaService()

    saida_salva = service.salvar(
        sequencia="1",
        data_saida=date(2026, 9, 12),
        itens_data=[
            {
                "produto_id": ctx["produto_id"],
                "quantidade": 20,
                "custo": 2.50,
            }
        ],
    )

    assert saida_salva.id is not None
    assert saida_salva.sequencia == "1"


def test_editar_saida_existente_atualiza_itens_com_diff(
    banco_sqlite_em_memoria,
):
    """Cobre o fluxo de edição: adicionar, atualizar e remover itens
    na mesma saída, validando o diff feito em _salvar_com_itens_inner."""
    ctx = banco_sqlite_em_memoria
    service = SaidaService()

    saida = service.salvar(
        sequencia="2",
        data_saida=date(2026, 9, 12),
        itens_data=[
            {"produto_id": ctx["produto_id"], "quantidade": 10, "custo": 2.5},
            {"produto_id": ctx["produto_id"], "quantidade": 5, "custo": 2.5},
        ],
    )

    _, itens_salvos = service.buscar_com_itens(saida.id)
    assert len(itens_salvos) == 2

    # Edição: atualiza o primeiro item, remove o segundo, adiciona um novo.
    itens_editados = [
        {
            "id": itens_salvos[0]["id"],
            "produto_id": ctx["produto_id"],
            "quantidade": 99,
            "custo": 3.0,
        },
        {"produto_id": ctx["produto_id"], "quantidade": 7, "custo": 2.5},
    ]

    service.salvar(
        sequencia="2",
        data_saida=date(2026, 9, 12),
        itens_data=itens_editados,
        saida_id=saida.id,
    )

    _, itens_finais = service.buscar_com_itens(saida.id)
    assert len(itens_finais) == 2
    quantidades = sorted(item["quantidade"] for item in itens_finais)
    assert quantidades == [7.0, 99.0]
