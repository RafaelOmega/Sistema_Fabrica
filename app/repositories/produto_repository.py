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

    def atualizar_custo(self, produto_id, novo_custo, session=None):
        """Atualiza o custo do produto.
        Se `session` for passada, usa-a (transação compartilhada) e
        NÃO desanexa o produto ao final, pois a transação ainda está
        em andamento e outro código pode precisar do objeto anexado
        depois. Caso contrário, abre, é dona da sessão e desanexa
        antes de retornar."""
        if session:
            return self._atualizar_custo_inner(
                session, produto_id, novo_custo, expunge=False
            )
        with session_scope() as session:
            return self._atualizar_custo_inner(
                session, produto_id, novo_custo, expunge=True
            )

    def _atualizar_custo_inner(self, session, produto_id, novo_custo,
                               expunge=True):
        produto = session.query(Produto).filter_by(id=produto_id).first()
        if not produto:
            return None
        custo_anterior = float(produto.custo) if produto.custo else 0.0
        produto.custo = novo_custo
        session.flush()
        session.refresh(produto)
        if expunge:
            session.expunge(produto)
        return custo_anterior

    def contar_vinculos(self, produto_id):
        """Conta vínculos do produto em entradas, saídas e fichas técnicas."""
        from app.models.entrada import ItemEntrada
        from app.models.saida import ItemSaida
        from app.models.ficha_tecnica import ItemFichaTecnica

        with session_scope() as session:
            return {
                "entradas": session.query(ItemEntrada)
                .filter_by(produto_id=produto_id).count(),
                "saidas": session.query(ItemSaida)
                .filter_by(produto_id=produto_id).count(),
                "fichas técnicas": session.query(ItemFichaTecnica)
                .filter_by(produto_id=produto_id).count(),
            }
