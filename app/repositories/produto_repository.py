from sqlalchemy.exc import IntegrityError

from app.database.connection import session_scope
from app.models.produto import Produto
from app.utils.logger import get_logger

logger = get_logger("produto_repository")


class ProdutoRepository:
    """Cada método abre sua própria sessão (via session_scope) e a fecha
    ao final, evitando sessões de vida longa presas ao controller/service."""

    def listar_todos(self):
        logger.debug("Listando todos os produtos")
        with session_scope() as session:
            produtos = session.query(Produto).order_by(Produto.id).all()
            session.expunge_all()
            return produtos

    def pesquisar(self, termo: str):
        logger.debug(f"Pesquisando produtos: termo='{termo}'")
        with session_scope() as session:
            produtos = (
                session.query(Produto)
                .filter(
                    (Produto.codigo.ilike(f"%{termo}%"))
                    | (Produto.descricao.ilike(f"%{termo}%"))
                )
                .all()
            )
            session.expunge_all()
            return produtos

    def buscar_por_id(self, produto_id: int):
        logger.debug(f"Buscando produto por ID={produto_id}")
        with session_scope() as session:
            produto = session.get(Produto, produto_id)
            if produto is not None:
                session.expunge(produto)
            return produto

    def buscar_por_codigo(self, codigo: str):
        logger.debug(f"Buscando produto por codigo='{codigo}'")
        with session_scope() as session:
            produto = session.query(Produto).filter(Produto.codigo == codigo).first()
            if produto is not None:
                session.expunge(produto)
            return produto

    def salvar(self, produto: Produto):
        """Persiste um produto (novo ou existente, desanexado de outra sessão).

        Levanta sqlalchemy.exc.IntegrityError se violar uma constraint
        (ex.: código duplicado inserido por outro usuário em paralelo).
        O rollback é feito automaticamente pelo session_scope.
        """
        logger.debug(f"Persistindo produto: codigo={produto.codigo}")
        with session_scope() as session:
            produto = session.merge(produto)
            try:
                session.flush()
            except IntegrityError:
                logger.warning(
                    f"Violação de integridade ao salvar produto: codigo={produto.codigo}"
                )
                raise
            session.refresh(produto)
            session.expunge(produto)
            return produto

    def excluir_por_id(self, produto_id: int) -> bool:
        """Exclui o produto pelo ID dentro de uma sessão própria.
        Retorna False se o produto não existir mais (ex.: já excluído por outro usuário)."""
        logger.debug(f"Excluindo produto ID={produto_id}")
        with session_scope() as session:
            produto = session.get(Produto, produto_id)
            if produto is None:
                return False
            session.delete(produto)
            return True
