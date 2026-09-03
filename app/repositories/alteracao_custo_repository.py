from app.database.connection import session_scope
from app.models.alteracao_custo import AlteracaoCusto


class AlteracaoCustoRepository:
    def registrar(self, codigo_produto, custo_anterior, custo_atual,
                  session=None):
        """Registra alteração de custo.
        Se session passada, usa-a (transação compartilhada)."""
        if session:
            return self._registrar_inner(
                session, codigo_produto, custo_anterior, custo_atual
            )
        with session_scope() as session:
            return self._registrar_inner(
                session, codigo_produto, custo_anterior, custo_atual
            )

    def _registrar_inner(self, session, codigo_produto, custo_anterior,
                         custo_atual):
        if custo_anterior == custo_atual:
            return None
        registro = AlteracaoCusto(
            codigo_produto=str(codigo_produto),
            custo_anterior=float(custo_anterior),
            custo_atual=float(custo_atual),
        )
        session.add(registro)
        session.flush()
        session.refresh(registro)
        session.expunge(registro)
        return registro

    def listar_por_produto(self, codigo_produto):
        with session_scope() as session:
            registros = (
                session.query(AlteracaoCusto)
                .filter_by(codigo_produto=codigo_produto)
                .order_by(AlteracaoCusto.data_alteracao.desc())
                .all()
            )
            for r in registros:
                session.expunge(r)
            return registros
