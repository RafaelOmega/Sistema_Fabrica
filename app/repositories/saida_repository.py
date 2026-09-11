from sqlalchemy import cast, func, Integer

from app.database.connection import session_scope
from app.models.produto import Produto
from app.models.saida import ItemSaida, Saida


class SaidaRepository:
    def listar_todos(self):
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
        """
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

    def buscar_com_itens(self, saida_id):
        """Retorna a saída e uma lista de dicts com dados dos itens
        já join com produto (codigo, descricao)."""
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
        """
        if session:
            return self._salvar_com_itens_inner(session, saida, itens_data)
        with session_scope() as session:
            return self._salvar_com_itens_inner(session, saida, itens_data)

    def _salvar_com_itens_inner(self, session, saida, itens_data):
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

        # 1. Excluir itens que não estão mais na lista
        for item_id, item in itens_existentes_map.items():
            if item_id not in ids_novos:
                session.delete(item)

        # 2. Atualizar existentes + inserir novos
        for item_data in itens_data:
            item_id = item_data.get("id")
            if item_id and item_id in itens_existentes_map:
                item = itens_existentes_map[item_id]
                item.produto_id = item_data["produto_id"]
                item.quantidade = item_data["quantidade"]
                item.custo = item_data["custo"]
            else:
                novo_item = ItemSaida(
                    saida_id=saida_persistida.id,
                    produto_id=item_data["produto_id"],
                    quantidade=item_data["quantidade"],
                    custo=item_data["custo"],
                )
                session.add(novo_item)

        session.flush()
        session.refresh(saida_persistida)
        session.expunge(saida_persistida)
        return saida_persistida

    def excluir_por_id(self, saida_id):
        with session_scope() as session:
            saida = session.query(Saida).filter_by(id=saida_id).first()
            if not saida:
                return False
            session.delete(saida)
            return True
