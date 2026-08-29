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

    logger.info("Criando tabelas no banco (se não existirem)")
    try:
        Base.metadata.create_all(engine)
        logger.info("Tabelas verificadas/criadas com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}", exc_info=True)
        raise


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
