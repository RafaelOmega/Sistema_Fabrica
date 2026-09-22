from sqlalchemy.exc import DataError

from app.database.connection import session_scope
from app.models.saida import Saida, ItemSaida
from app.models.produto import Produto
from app.models.movimento_estoque import TIPO_SAIDA
from app.repositories.movimento_estoque_repository import (
    MovimentoEstoqueRepository,
)


class SaidaRepository:
    def __init__(self):
        self.movimento_repo = MovimentoEstoqueRepository()

    def listar_todos(self):
        """Lista todas as saídas."""
        with session_scope() as session:
            saidas = (
                session.query(Saida)
                .order_by(Saida.id.desc())
                .all()
            )

            resultado = []
            for saida in saidas:
                session.expunge(saida)
                resultado.append({
                    "id": saida.id,
                    "sequencia": saida.sequencia,
                    "data_saida": saida.data_saida,
                })
            return resultado

    def buscar_por_id(self, saida_id):
        with session_scope() as session:
            saida = session.query(Saida).filter_by(id=saida_id).first()
            if saida:
                session.expunge(saida)
            return saida

    def buscar_por_sequencia(self, sequencia):
        with session_scope() as session:
            saida = (
                session.query(Saida)
                .filter_by(sequencia=sequencia)
                .first()
            )
            if saida:
                session.expunge(saida)
            return saida

    def obter_proxima_sequencia(self):
        """
        Retorna o próximo código baseado no maior código numérico existente.
        Usa func.max no banco em vez de carregar todas as sequências.
        Previne colisão quando o último registro é deletado.
        """
        from sqlalchemy import cast, func, Integer

        try:
            with session_scope() as session:
                max_seq = (
                    session.query(
                        func.max(cast(Saida.sequencia, Integer))
                    )
                    .scalar()
                )
                if max_seq is None:
                    return "1"
                return str(max_seq + 1)
        except DataError:
            # Alguma sequência existente no banco não é puramente
            # numérica. Convertemos o erro de SQL em uma mensagem
            # compreensível em vez de deixar a exceção crua do driver
            # subir à UI.
            raise ValueError(
                "Não foi possível calcular a próxima sequência: existe "
                "uma sequência de saída cadastrada com valor não "
                "numérico. Corrija o cadastro antes de continuar."
            )

    def buscar_com_itens(self, saida_id):
        """Retorna a saída e uma lista de dicts com dados dos itens
        já com join com produto (codigo, descricao)."""
        with session_scope() as session:
            saida = session.query(Saida).filter_by(id=saida_id).first()
            if not saida:
                return None, []

            itens_query = (
                session.query(
                    ItemSaida,
                    Produto.codigo,
                    Produto.descricao,
                )
                .join(Produto, ItemSaida.produto_id == Produto.id)
                .filter(ItemSaida.saida_id == saida_id)
                .all()
            )

            session.expunge(saida)
            itens = []
            for item, codigo, descricao in itens_query:
                session.expunge(item)
                itens.append({
                    "id": item.id,
                    "produto_id": item.produto_id,
                    "codigo": codigo,
                    "descricao": descricao,
                    "quantidade": float(item.quantidade)
                    if item.quantidade else 0.0,
                    "custo": float(item.custo) if item.custo else 0.0,
                })
            return saida, itens

    def salvar_com_itens(self, saida, itens_data, session=None):
        """
        Salva a saída e seus itens usando diff (inserir/atualizar/excluir).

        itens_data: lista de dicts. Itens com 'id' são atualizados;
        itens sem 'id' são inseridos; itens existentes não presentes
        são excluídos.

        Se `session` for passada, usa-a (para transação compartilhada)
        e NÃO desanexa (expunge) a saída ao final — a transação ainda
        está em andamento e o chamador (quem passou a session) é
        responsável por isso quando terminar seu próprio trabalho.
        Caso contrário, cria e é dona de uma nova session_scope(), e aí
        sim desanexa a saída antes de retornar, pois o "with" está
        prestes a fechar a sessão.
        """
        if session:
            return self._salvar_com_itens_inner(
                session, saida, itens_data, expunge=False
            )
        with session_scope() as session:
            return self._salvar_com_itens_inner(
                session, saida, itens_data, expunge=True
            )

    def _salvar_com_itens_inner(self, session, saida, itens_data,
                                 expunge=True):
        """Lógica interna de diff de itens + sincronização do kardex."""
        saida_persistida = session.merge(saida)
        session.flush()

        itens_existentes = (
            session.query(ItemSaida)
            .filter_by(saida_id=saida_persistida.id)
            .all()
        )
        itens_existentes_map = {item.id: item for item in itens_existentes}

        ids_novos = {
            item["id"] for item in itens_data
            if item.get("id") is not None
        }

        # 1. Excluir itens que não estão mais na lista (+ seu
        # movimento de kardex).
        for item_id, item in itens_existentes_map.items():
            if item_id not in ids_novos:
                self.movimento_repo.excluir_por_origem(
                    session, "itens_saida", item_id
                )
                session.delete(item)

        # 2. Atualizar existentes + inserir novos.
        itens_para_kardex = []
        for item_data in itens_data:
            item_id = item_data.get("id")
            if item_id and item_id in itens_existentes_map:
                item = itens_existentes_map[item_id]
                item.produto_id = item_data["produto_id"]
                item.quantidade = item_data["quantidade"]
                item.custo = item_data["custo"]
            else:
                item = ItemSaida(
                    saida_id=saida_persistida.id,
                    produto_id=item_data["produto_id"],
                    quantidade=item_data["quantidade"],
                    custo=item_data["custo"],
                )
                session.add(item)
            itens_para_kardex.append(item)

        session.flush()
        session.refresh(saida_persistida)

        # 3. Sincronizar o kardex com o estado final dos itens desta
        # saída.
        for item in itens_para_kardex:
            self.movimento_repo.registrar_ou_atualizar(
                session,
                origem_tabela="itens_saida",
                origem_id=item.id,
                produto_id=item.produto_id,
                quantidade=float(item.quantidade),
                custo_unitario=float(item.custo),
                data_movimento=saida_persistida.data_saida,
                tipo=TIPO_SAIDA,
            )

        if expunge:
            session.expunge(saida_persistida)
        return saida_persistida

    def excluir_por_id(self, saida_id):
        with session_scope() as session:
            saida = session.query(Saida).filter_by(id=saida_id).first()
            if not saida:
                return False

            itens = (
                session.query(ItemSaida)
                .filter_by(saida_id=saida_id)
                .all()
            )
            for item in itens:
                self.movimento_repo.excluir_por_origem(
                    session, "itens_saida", item.id
                )

            session.delete(saida)
            return True
