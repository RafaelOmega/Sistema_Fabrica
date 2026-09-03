from app.database.connection import session_scope
from app.models.entrada import Entrada, ItemEntrada
from app.models.motivo_entrada import Motivo_Entrada
from app.models.produto import Produto


class EntradaRepository:
    def listar_todos(self):
        """Lista todas as entradas com a descrição do motivo."""
        with session_scope() as session:
            resultados = (
                session.query(
                    Entrada,
                    Motivo_Entrada.descricao.label("motivo_descricao")
                )
                .outerjoin(
                    Motivo_Entrada,
                    Entrada.motivo_entrada_id == Motivo_Entrada.id
                )
                .order_by(Entrada.id.desc())
                .all()
            )

            entradas = []
            for entrada, motivo_descricao in resultados:
                session.expunge(entrada)
                entradas.append({
                    "id": entrada.id,
                    "sequencia": entrada.sequencia,
                    "data_entrada": entrada.data_entrada,
                    "motivo_descricao": motivo_descricao or "",
                })
            return entradas

    def buscar_por_id(self, entrada_id):
        with session_scope() as session:
            entrada = session.query(Entrada).filter_by(id=entrada_id).first()
            if entrada:
                session.expunge(entrada)
            return entrada

    def buscar_por_sequencia(self, sequencia):
        with session_scope() as session:
            entrada = (
                session.query(Entrada)
                .filter_by(sequencia=sequencia)
                .first()
            )
            if entrada:
                session.expunge(entrada)
            return entrada

    def obter_proxima_sequencia(self):
        """
        Retorna o próximo código baseado no maior código numérico existente.
        Previne colisão quando o último registro é deletado.
        """
        with session_scope() as session:
            sequencias = session.query(Entrada.sequencia).all()
            if not sequencias:
                return "1"

            numeros = []
            for (seq,) in sequencias:
                try:
                    numeros.append(int(seq))
                except (ValueError, TypeError):
                    continue

            if not numeros:
                return "1"

            return str(max(numeros) + 1)

    def buscar_com_itens(self, entrada_id):
        """Retorna a entrada e uma lista de dicts com dados dos itens
        já join com produto (codigo, descricao)."""
        with session_scope() as session:
            entrada = session.query(Entrada).filter_by(id=entrada_id).first()
            if not entrada:
                return None, []

            itens_query = (
                session.query(
                    ItemEntrada,
                    Produto.codigo,
                    Produto.descricao,
                )
                .join(Produto, ItemEntrada.produto_id == Produto.id)
                .filter(ItemEntrada.entrada_id == entrada_id)
                .all()
            )

            session.expunge(entrada)
            itens = []
            for item, codigo, descricao in itens_query:
                session.expunge(item)
                itens.append({
                    "id": item.id,
                    "produto_id": item.produto_id,
                    "codigo": codigo,
                    "descricao": descricao,
                    "unidade": item.unidade,
                    "quantidade": float(item.quantidade)
                    if item.quantidade else 0.0,
                    "custo": float(item.custo) if item.custo else 0.0,
                })
            return entrada, itens

    def salvar_com_itens(self, entrada, itens_data, session=None):
        """
        Salva a entrada e seus itens usando diff (inserir/atualizar/excluir).

        itens_data: lista de dicts. Itens com 'id' são atualizados;
        itens sem 'id' são inseridos; itens existentes não presentes
        são excluídos.

        Se `session` for passada, usa-a (para transação compartilhada).
        Caso contrário, cria uma nova session_scope().
        """
        if session:
            return self._salvar_com_itens_inner(session, entrada, itens_data)
        with session_scope() as session:
            return self._salvar_com_itens_inner(session, entrada, itens_data)

    def _salvar_com_itens_inner(self, session, entrada, itens_data):
        """Lógica interna de diff de itens."""
        entrada_persistida = session.merge(entrada)
        session.flush()

        # Buscar itens existentes
        itens_existentes = (
            session.query(ItemEntrada)
            .filter_by(entrada_id=entrada_persistida.id)
            .all()
        )
        itens_existentes_map = {item.id: item for item in itens_existentes}

        # IDs dos itens novos que já têm ID (vêm de edição)
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
                # Atualizar item existente
                item = itens_existentes_map[item_id]
                item.produto_id = item_data["produto_id"]
                item.unidade = item_data["unidade"]
                item.quantidade = item_data["quantidade"]
                item.custo = item_data["custo"]
            else:
                # Inserir novo item
                novo_item = ItemEntrada(
                    entrada_id=entrada_persistida.id,
                    produto_id=item_data["produto_id"],
                    unidade=item_data["unidade"],
                    quantidade=item_data["quantidade"],
                    custo=item_data["custo"],
                )
                session.add(novo_item)

        session.flush()
        session.refresh(entrada_persistida)
        session.expunge(entrada_persistida)
        return entrada_persistida

    def excluir_por_id(self, entrada_id):
        with session_scope() as session:
            entrada = session.query(Entrada).filter_by(id=entrada_id).first()
            if not entrada:
                return False
            session.delete(entrada)
            return True
