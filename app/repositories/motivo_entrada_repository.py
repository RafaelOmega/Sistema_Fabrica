from sqlalchemy import or_, func
from sqlalchemy.exc import DataError

from app.database.connection import session_scope
from app.models.motivo_entrada import Motivo_Entrada


class MotivoEntradaRepository:
    def listar_todos(self):
        with session_scope() as session:
            motivos = (
                session.query(Motivo_Entrada)
                .order_by(Motivo_Entrada.descricao.asc())
                .all()
            )
            session.expunge_all()
            return motivos

    def pesquisar(self, termo):
        termo = (termo or "").strip()

        with session_scope() as session:
            query = session.query(Motivo_Entrada)

            if termo:
                filtro = f"%{termo}%"
                query = query.filter(
                    or_(
                        Motivo_Entrada.codigo.ilike(filtro),
                        Motivo_Entrada.descricao.ilike(filtro),
                    )
                )

            motivos = query.order_by(Motivo_Entrada.descricao.asc()).all()
            session.expunge_all()
            return motivos

    def buscar_por_id(self, motivo_id):
        with session_scope() as session:
            motivo = (
                session.query(Motivo_Entrada)
                .filter_by(id=motivo_id)
                .first()
            )
            if motivo:
                session.expunge(motivo)
            return motivo

    def buscar_por_codigo(self, codigo):
        with session_scope() as session:
            motivo = (
                session.query(Motivo_Entrada)
                .filter_by(codigo=codigo)
                .first()
            )
            if motivo:
                session.expunge(motivo)
            return motivo

    def obter_proximo_codigo(self):
        """
        Retorna o próximo código baseado no maior código numérico existente.
        Usa func.max no banco em vez de carregar todos os códigos.
        Previne colisão quando o último registro é deletado.
        """
        from sqlalchemy import cast, func, Integer

        try:
            with session_scope() as session:
                max_codigo = (
                    session.query(
                        func.max(cast(Motivo_Entrada.codigo, Integer))
                    )
                    .scalar()
                )
                if max_codigo is None:
                    return "1"
                return str(max_codigo + 1)
        except DataError:
            # Algum código existente no banco não é puramente numérico.
            # Convertemos o erro de SQL em mensagem compreensível.
            raise ValueError(
                "Não foi possível calcular o próximo código: existe um "
                "motivo de entrada cadastrado com código não numérico. "
                "Corrija o cadastro antes de continuar."
            )

    def salvar(self, motivo):
        with session_scope() as session:
            motivo_persistido = session.merge(motivo)
            session.flush()
            session.refresh(motivo_persistido)
            session.expunge(motivo_persistido)
            return motivo_persistido

    def excluir_por_id(self, motivo_id):
        with session_scope() as session:
            motivo = (
                session.query(Motivo_Entrada)
                .filter_by(id=motivo_id)
                .first()
            )

            if not motivo:
                return False

            session.delete(motivo)
            return True
