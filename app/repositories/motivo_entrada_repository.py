from sqlalchemy import or_, func

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
        Previne colisão quando o último registro é deletado.
        """
        with session_scope() as session:
            codigos = session.query(Motivo_Entrada.codigo).all()
            if not codigos:
                return "1"

            numeros = []
            for (codigo,) in codigos:
                try:
                    numeros.append(int(codigo))
                except (ValueError, TypeError):
                    continue

            if not numeros:
                return "1"

            return str(max(numeros) + 1)

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
