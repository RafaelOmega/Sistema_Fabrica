from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL
from app.database.base import Base
from app.utils.logger import get_logger

logger = get_logger("database")

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
Session = sessionmaker(bind=engine)


def init_db():
    """Cria todas as tabelas no banco."""
    from app.models.produto import Produto  # noqa: F401
    from app.models.motivo_entrada import Motivo_Entrada  # noqa: F401
    from app.models.entrada import Entrada, ItemEntrada  # noqa: F401
    from app.models.alteracao_custo import AlteracaoCusto  # noqa: F401
    from app.models.ficha_tecnica import (  # noqa: F401
        FichaTecnica, ItemFichaTecnica,
    )
    from app.models.consumo_producao import ConsumoProducao  # noqa: F401
    from app.models.regra_produto_especial import (  # noqa: F401
        RegraProdutoEspecial,
    )
    from app.models.saida import Saida, ItemSaida  # noqa: F401
    from app.models.movimento_estoque import MovimentoEstoque  # noqa: F401

    logger.info("Criando tabelas no banco (se não existirem)")
    try:
        Base.metadata.create_all(engine)
        logger.info("Tabelas verificadas/criadas com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}", exc_info=True)
        raise

    _migrar_regras_produtos_especiais_padrao()
    _migrar_colunas_produto()
    _migrar_colunas_motivo_entrada()


def _migrar_colunas_produto():
    """Adiciona colunas novas na tabela produtos para instalações que
    já existiam antes desta versão.

    Base.metadata.create_all() só CRIA tabelas que não existem — não
    altera tabelas já existentes para adicionar colunas novas. Como
    `mao_obra` e `controla_estoque` foram adicionadas ao modelo
    Produto depois que o sistema já estava em produção, precisamos
    dessa migração leve para não quebrar bancos já existentes.
    """
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    colunas_existentes = {
        col["name"] for col in inspector.get_columns("produtos")
    }

    colunas_novas = {
        "mao_obra": (
            "ALTER TABLE produtos ADD COLUMN mao_obra "
            "BOOLEAN NOT NULL DEFAULT false"
        ),
        "controla_estoque": (
            "ALTER TABLE produtos ADD COLUMN controla_estoque "
            "BOOLEAN NOT NULL DEFAULT false"
        ),
    }

    for coluna, ddl in colunas_novas.items():
        if coluna not in colunas_existentes:
            logger.info(f"Adicionando coluna produtos.{coluna}")
            with engine.begin() as conn:
                conn.execute(text(ddl))


def _migrar_regras_produtos_especiais_padrao():
    """Semente única: garante que a regra que antes vivia fixa no código
    (REGRAS_PRODUTOS_ESPECIAIS em entrada_service.py) continue existindo
    depois da migração para a tabela regras_produtos_especiais.

    Só insere se a tabela estiver vazia, então não sobrescreve edições
    feitas pelo usuário depois da migração inicial.
    """
    from app.models.regra_produto_especial import RegraProdutoEspecial

    with session_scope() as session:
        existe_alguma = session.query(RegraProdutoEspecial).first()
        if existe_alguma:
            return

        logger.info(
            "Semeando regra padrão de produto especial (Milho 60KG) "
            "na tabela regras_produtos_especiais"
        )
        session.add(
            RegraProdutoEspecial(
                codigo_produto="116431",
                descricao="Milho 60KG",
                divisor_custo=60,
            )
        )


def _migrar_colunas_motivo_entrada():
    """Adiciona a coluna producao em motivos_entrada para instalações
    que já existiam antes desta versão (create_all não altera tabelas
    existentes)."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    colunas_existentes = {
        col["name"] for col in inspector.get_columns("motivos_entrada")
    }

    if "producao" not in colunas_existentes:
        logger.info("Adicionando coluna motivos_entrada.producao")
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE motivos_entrada ADD COLUMN "
                "producao BOOLEAN NOT NULL DEFAULT false"
            ))


def get_session():
    """Cria uma sessão avulsa. Prefira session_scope() sempre que possível,
    pois ele garante commit/rollback/close automáticos."""
    session = Session()
    logger.debug("Nova sessão do banco criada")
    return session


@contextmanager
def session_scope():
    """Fornece uma sessão com commit automático em caso de sucesso,
    rollback em caso de exceção e close garantido no final.

    Uso:
        with session_scope() as session:
            session.add(objeto)
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        logger.warning(
            "Sessão revertida (rollback) devido a um erro", exc_info=True)
        raise
    finally:
        session.close()
