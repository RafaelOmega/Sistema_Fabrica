from app.database.connection import session_scope
from app.models.regra_produto_especial import RegraProdutoEspecial


class RegraProdutoEspecialRepository:
    def listar_todos(self):
        with session_scope() as session:
            regras = (
                session.query(RegraProdutoEspecial)
                .order_by(RegraProdutoEspecial.codigo_produto.asc())
                .all()
            )
            session.expunge_all()
            return regras

    def buscar_por_id(self, regra_id):
        with session_scope() as session:
            regra = (
                session.query(RegraProdutoEspecial)
                .filter_by(id=regra_id)
                .first()
            )
            if regra:
                session.expunge(regra)
            return regra

    def buscar_por_codigo(self, codigo_produto):
        with session_scope() as session:
            regra = (
                session.query(RegraProdutoEspecial)
                .filter_by(codigo_produto=codigo_produto)
                .first()
            )
            if regra:
                session.expunge(regra)
            return regra

    def salvar(self, codigo_produto, descricao, divisor_custo, regra_id=None):
        with session_scope() as session:
            if regra_id is None:
                regra = RegraProdutoEspecial()
            else:
                regra = session.query(RegraProdutoEspecial).filter_by(
                    id=regra_id
                ).first()
                if not regra:
                    raise ValueError(
                        "Regra de produto especial não encontrada."
                    )

            regra.codigo_produto = codigo_produto
            regra.descricao = descricao
            regra.divisor_custo = divisor_custo

            session.add(regra)
            session.flush()
            session.refresh(regra)
            session.expunge(regra)
            return regra

    def excluir_por_id(self, regra_id):
        with session_scope() as session:
            regra = (
                session.query(RegraProdutoEspecial)
                .filter_by(id=regra_id)
                .first()
            )
            if not regra:
                return False
            session.delete(regra)
            return True
