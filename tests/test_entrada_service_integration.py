"""
Teste de INTEGRAÇÃO (SQLite real em memória, sem mocks) para o fluxo
completo de EntradaService.salvar() com alteração de custo.

Por quê um teste separado dos demais (que usam MagicMock)?
----------------------------------------------------------
O bug corrigido aqui (Session.merge()/expunge() em transação
compartilhada — ver commits em entrada_repository.py,
produto_repository.py e alteracao_custo_repository.py) é um bug de
CICLO DE VIDA REAL da Session do SQLAlchemy: um objeto sendo
desanexado (expunge) no meio de uma transação que outro código ainda
precisa usar. Testes com MagicMock não exercitam esse mecanismo (o
mock não tem noção de "objeto anexado/desanexado de uma sessão"), por
isso não pegam esse tipo de regressão. Este teste usa um banco SQLite
real em memória para reproduzir o cenário de ponta a ponta, do jeito
que aconteceu em produção (alteração de custo do produto 116431 no
log de 12/09/2026).
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


@pytest.fixture
def banco_sqlite_em_memoria(monkeypatch):
    """Cria um banco SQLite em memória com o schema real da aplicação
    e substitui `session_scope` por uma versão que usa esse banco."""
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

    # Popula dados de apoio (motivo de entrada + produto), usando o
    # mesmo engine/sessionmaker, fora do fluxo em teste.
    with SessionLocal() as setup_session:
        motivo = Motivo_Entrada(codigo="1", descricao="Compra")
        produto = Produto(
            codigo="116431",
            descricao="Milho 60KG",
            peso=60.0,
            custo=1.1500,
            prod_acabado=False,
            mat_prima=True,
        )
        setup_session.add_all([motivo, produto])
        setup_session.commit()
        setup_session.refresh(motivo)
        setup_session.refresh(produto)
        motivo_id = motivo.id
        produto_id = produto.id

    return {"motivo_id": motivo_id, "produto_id": produto_id}


def test_salvar_com_alteracao_de_custo_nao_quebra_a_sessao(
    banco_sqlite_em_memoria,
):
    """
    Reproduz o cenário exato do log de produção: uma entrada nova,
    com um item cujo custo mudou em relação ao custo atual do
    produto, disparando o registro de alteração de custo + update do
    produto na MESMA transação da entrada.

    Antes da correção, isso lançava:
        sqlalchemy.exc.InvalidRequestError: Instance '<Entrada ...>'
        is not persistent within this Session
    porque `EntradaRepository._salvar_com_itens_inner` desanexava
    (`session.expunge`) o objeto `entrada` da sessão compartilhada
    antes do `EntradaService.salvar()` terminar de usá-la.
    """
    ctx = banco_sqlite_em_memoria
    service = EntradaService()

    entrada_salva = service.salvar_com_alteracao_custo(
        sequencia="1",
        data_entrada=date(2026, 9, 12),
        motivo_id=ctx["motivo_id"],
        itens_data=[
            {
                "produto_id": ctx["produto_id"],
                "unidade": "SC",
                "quantidade": 100,
                "custo": 1.1667,
            }
        ],
        alteracoes_custo=[
            {
                "codigo_produto": "116431",
                "produto_id": ctx["produto_id"],
                "custo_anterior": 1.1500,
                "custo_atual": 1.1667,
            }
        ],
    )

    # Não deve levantar InvalidRequestError, e a entrada deve ter sido
    # persistida com sucesso (id atribuído pelo banco).
    assert entrada_salva.id is not None
    assert entrada_salva.sequencia == "1"


def test_produto_reflete_novo_custo_apos_salvar(banco_sqlite_em_memoria):
    """O custo do produto deve ser atualizado na mesma transação."""
    from sqlalchemy import create_engine as _ce  # apenas para leitura
    ctx = banco_sqlite_em_memoria
    service = EntradaService()

    service.salvar_com_alteracao_custo(
        sequencia="2",
        data_entrada=date(2026, 9, 12),
        motivo_id=ctx["motivo_id"],
        itens_data=[
            {
                "produto_id": ctx["produto_id"],
                "unidade": "SC",
                "quantidade": 50,
                "custo": 1.2000,
            }
        ],
        alteracoes_custo=[
            {
                "codigo_produto": "116431",
                "produto_id": ctx["produto_id"],
                "custo_anterior": 1.1500,
                "custo_atual": 1.2000,
            }
        ],
    )

    from app.database.connection import session_scope
    with session_scope() as session:
        produto = session.query(Produto).filter_by(
            id=ctx["produto_id"]
        ).first()
        assert float(produto.custo) == pytest.approx(1.2000)
