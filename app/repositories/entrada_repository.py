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
        with session_scope() as session:
            ultimo = (
                session.query(Entrada.sequencia)
                .order_by(Entrada.id.desc())
                .first()
            )

            if not ultimo:
                return "1"

            try:
                proximo = int(ultimo[0]) + 1
                return str(proximo)
            except (ValueError, TypeError):
                count = session.query(Entrada).count()
                return str(count + 1)

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

    def salvar_com_itens(self, entrada, itens_data):
        """Salva a entrada e substitui todos os itens em uma transação."""
        with session_scope() as session:
            entrada_persistida = session.merge(entrada)
            session.flush()

            session.query(ItemEntrada).filter_by(
                entrada_id=entrada_persistida.id
            ).delete()

            for item_data in itens_data:
                item = ItemEntrada(
                    entrada_id=entrada_persistida.id,
                    produto_id=item_data["produto_id"],
                    unidade=item_data["unidade"],
                    quantidade=item_data["quantidade"],
                    custo=item_data["custo"],
                )
                session.add(item)

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
