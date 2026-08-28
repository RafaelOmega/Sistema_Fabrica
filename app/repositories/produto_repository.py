from sqlalchemy import or_

from app.database.connection import session_scope
from app.models.produto import Produto


class ProdutoRepository:
    def listar_todos(self):
        with session_scope() as session:
            produtos = (
                session.query(Produto)
                .order_by(Produto.descricao.asc())
                .all()
            )
            session.expunge_all()
            return produtos

    def pesquisar(self, termo):
        termo = (termo or "").strip()

        with session_scope() as session:
            query = session.query(Produto)

            if termo:
                filtro = f"%{termo}%"
                query = query.filter(
                    or_(
                        Produto.codigo.ilike(filtro),
                        Produto.descricao.ilike(filtro),
                    )
                )

            produtos = query.order_by(Produto.descricao.asc()).all()
            session.expunge_all()
            return produtos

    def buscar_por_id(self, produto_id):
        with session_scope() as session:
            produto = session.query(Produto).filter_by(id=produto_id).first()
            if produto:
                session.expunge(produto)
            return produto

    def buscar_por_codigo(self, codigo):
        with session_scope() as session:
            produto = session.query(Produto).filter_by(codigo=codigo).first()
            if produto:
                session.expunge(produto)
            return produto

    def salvar(self, produto):
        with session_scope() as session:
            produto_persistido = session.merge(produto)
            session.flush()
            session.refresh(produto_persistido)
            session.expunge(produto_persistido)
            return produto_persistido

    def excluir_por_id(self, produto_id):
        with session_scope() as session:
            produto = session.query(Produto).filter_by(id=produto_id).first()

            if not produto:
                return False

            session.delete(produto)
            return True
