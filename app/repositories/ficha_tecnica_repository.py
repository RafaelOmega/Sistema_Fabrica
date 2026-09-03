from app.database.connection import session_scope
from app.models.ficha_tecnica import FichaTecnica, ItemFichaTecnica
from app.models.produto import Produto


class FichaTecnicaRepository:
    def buscar_por_id(self, ficha_id):
        with session_scope() as session:
            ficha = (
                session.query(FichaTecnica)
                .filter_by(id=ficha_id)
                .first()
            )
            if ficha:
                session.expunge(ficha)
            return ficha

    def buscar_por_produto_acabado_id(self, produto_acabado_id):
        with session_scope() as session:
            ficha = (
                session.query(FichaTecnica)
                .filter_by(produto_acabado_id=produto_acabado_id)
                .first()
            )
            if ficha:
                session.expunge(ficha)
            return ficha

    def buscar_com_itens(self, ficha_id):
        """Retorna a ficha e uma lista de dicts com os itens já
        join com produto (código, descrição) da matéria-prima."""
        with session_scope() as session:
            ficha = session.query(FichaTecnica).filter_by(id=ficha_id).first()
            if not ficha:
                return None, []

            itens_query = (
                session.query(
                    ItemFichaTecnica,
                    Produto.codigo,
                    Produto.descricao,
                )
                .join(Produto, ItemFichaTecnica.materia_prima_id == Produto.id)
                .filter(ItemFichaTecnica.ficha_tecnica_id == ficha_id)
                .all()
            )

            session.expunge(ficha)
            itens = []
            for item, codigo, descricao in itens_query:
                session.expunge(item)
                itens.append({
                    "id": item.id,
                    "materia_prima_id": item.materia_prima_id,
                    "codigo": codigo,
                    "descricao": descricao,
                    "quantidade": float(item.quantidade)
                    if item.quantidade else 0.0,
                })
            return ficha, itens

    def salvar_com_itens(self, ficha, itens_data, session=None):
        """
        Salva a ficha técnica e seus itens usando diff
        (inserir/atualizar/excluir).

        itens_data: lista de dicts. Itens com 'id' são atualizados;
        itens sem 'id' são inseridos; itens existentes não presentes
        são excluídos.

        Se `session` for passada, usa-a (para transação compartilhada).
        Caso contrário, cria uma nova session_scope().
        """
        if session:
            return self._salvar_com_itens_inner(session, ficha, itens_data)
        with session_scope() as session:
            return self._salvar_com_itens_inner(session, ficha, itens_data)

    def _salvar_com_itens_inner(self, session, ficha, itens_data):
        ficha_persistida = session.merge(ficha)
        session.flush()

        itens_existentes = (
            session.query(ItemFichaTecnica)
            .filter_by(ficha_tecnica_id=ficha_persistida.id)
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
                item.materia_prima_id = item_data["materia_prima_id"]
                item.quantidade = item_data["quantidade"]
            else:
                novo_item = ItemFichaTecnica(
                    ficha_tecnica_id=ficha_persistida.id,
                    materia_prima_id=item_data["materia_prima_id"],
                    quantidade=item_data["quantidade"],
                )
                session.add(novo_item)

        session.flush()
        session.refresh(ficha_persistida)
        session.expunge(ficha_persistida)
        return ficha_persistida

    def excluir_por_id(self, ficha_id):
        with session_scope() as session:
            ficha = session.query(FichaTecnica).filter_by(id=ficha_id).first()
            if not ficha:
                return False
            session.delete(ficha)
            return True
