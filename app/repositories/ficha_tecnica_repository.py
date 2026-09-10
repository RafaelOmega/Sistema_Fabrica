from app.database.connection import session_scope
from app.models.ficha_tecnica import FichaTecnica, ItemFichaTecnica
from app.models.produto import Produto


class FichaTecnicaRepository:
    def listar_todos(self):
        """Lista todas as fichas técnicas com dados do produto acabado."""
        with session_scope() as session:
            resultados = (
                session.query(
                    FichaTecnica,
                    Produto.codigo,
                    Produto.descricao,
                )
                .join(Produto, FichaTecnica.produto_id == Produto.id)
                .order_by(FichaTecnica.id.desc())
                .all()
            )

            fichas = []
            for ficha, codigo, descricao in resultados:
                session.expunge(ficha)
                fichas.append({
                    "id": ficha.id,
                    "produto_id": ficha.produto_id,
                    "codigo": codigo,
                    "descricao": descricao,
                    "sacos_batida": ficha.sacos_batida,
                })
            return fichas

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

    def buscar_por_produto(self, produto_id):
        with session_scope() as session:
            ficha = (
                session.query(FichaTecnica)
                .filter_by(produto_id=produto_id)
                .first()
            )
            if ficha:
                session.expunge(ficha)
            return ficha

    def buscar_com_itens(self, ficha_id):
        """Retorna a ficha e uma lista de dicts com dados dos itens
        já join com produto (codigo, descricao)."""
        with session_scope() as session:
            ficha = (
                session.query(FichaTecnica)
                .filter_by(id=ficha_id)
                .first()
            )
            if not ficha:
                return None, []

            itens_query = (
                session.query(
                    ItemFichaTecnica,
                    Produto.codigo,
                    Produto.descricao,
                )
                .join(
                    Produto,
                    ItemFichaTecnica.produto_id == Produto.id,
                )
                .filter(ItemFichaTecnica.ficha_id == ficha_id)
                .all()
            )

            session.expunge(ficha)
            itens = []
            for item, codigo, descricao in itens_query:
                session.expunge(item)
                itens.append({
                    "id": item.id,
                    "produto_id": item.produto_id,
                    "codigo": codigo,
                    "codigo_produto": item.codigo_produto,  # ← ADICIONADO
                    "descricao": descricao,
                    "quantidade_kg": float(item.quantidade_kg)
                    if item.quantidade_kg
                    else 0.0,
                })
            return ficha, itens

    def salvar_com_itens(self, ficha, itens_data, session=None):
        """
        Salva a ficha e seus itens usando diff (inserir/atualizar/excluir).
        """
        if session:
            return self._salvar_com_itens_inner(session, ficha, itens_data)
        with session_scope() as session:
            return self._salvar_com_itens_inner(
                session, ficha, itens_data
            )

    def _salvar_com_itens_inner(self, session, ficha, itens_data):
        """Lógica interna de diff de itens."""
        ficha_persistida = session.merge(ficha)
        session.flush()

        itens_existentes = (
            session.query(ItemFichaTecnica)
            .filter_by(ficha_id=ficha_persistida.id)
            .all()
        )
        itens_existentes_map = {
            item.id: item for item in itens_existentes
        }

        ids_novos = {
            item["id"]
            for item in itens_data
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
                item.codigo_produto = item_data.get(
                    "codigo_produto", "")  # ← ADICIONADO
                item.quantidade_kg = item_data["quantidade_kg"]
            else:
                novo_item = ItemFichaTecnica(
                    ficha_id=ficha_persistida.id,
                    produto_id=item_data["produto_id"],
                    codigo_produto=item_data.get(
                        "codigo_produto", ""),  # ← ADICIONADO
                    quantidade_kg=item_data["quantidade_kg"],
                )
                session.add(novo_item)

        session.flush()
        session.refresh(ficha_persistida)
        session.expunge(ficha_persistida)
        return ficha_persistida

    def excluir_por_id(self, ficha_id):
        with session_scope() as session:
            ficha = (
                session.query(FichaTecnica)
                .filter_by(id=ficha_id)
                .first()
            )
            if not ficha:
                return False
            session.delete(ficha)
            return True
