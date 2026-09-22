from sqlalchemy.exc import DataError

from app.database.connection import session_scope
from app.models.entrada import Entrada, ItemEntrada
from app.models.motivo_entrada import Motivo_Entrada
from app.models.movimento_estoque import TIPO_ENTRADA
from app.models.produto import Produto
from app.repositories.movimento_estoque_repository import (
    MovimentoEstoqueRepository,
)


class EntradaRepository:
    def __init__(self):
        self.movimento_repo = MovimentoEstoqueRepository()

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
        Usa func.max no banco em vez de carregar todas as sequências.
        Previne colisão quando o último registro é deletado.
        """
        from sqlalchemy import cast, func, Integer

        try:
            with session_scope() as session:
                max_seq = (
                    session.query(
                        func.max(cast(Entrada.sequencia, Integer))
                    )
                    .scalar()
                )
                if max_seq is None:
                    return "1"
                return str(max_seq + 1)
        except DataError:
            # Alguma sequência existente no banco não é puramente
            # numérica (não deveria acontecer com a validação do
            # service, mas pode ocorrer com dados antigos/importados).
            # Convertemos o erro de SQL em uma mensagem compreensível
            # em vez de deixar a exceção crua do driver subir à UI.
            raise ValueError(
                "Não foi possível calcular a próxima sequência: existe "
                "uma sequência cadastrada com valor não numérico. "
                "Corrija o cadastro antes de continuar."
            )

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

        Se `session` for passada, usa-a (para transação compartilhada)
        e NÃO desanexa (expunge) a entrada ao final — a transação
        ainda está em andamento e o chamador (quem passou a session)
        é responsável por isso quando terminar seu próprio trabalho.
        Caso contrário, cria e é dona de uma nova session_scope(), e aí
        sim desanexa a entrada antes de retornar, pois o "with" está
        prestes a fechar a sessão.
        """
        if session:
            return self._salvar_com_itens_inner(
                session, entrada, itens_data, expunge=False
            )
        with session_scope() as session:
            return self._salvar_com_itens_inner(
                session, entrada, itens_data, expunge=True
            )

    def _salvar_com_itens_inner(self, session, entrada, itens_data,
                                expunge=True):
        """Lógica interna de diff de itens + sincronização do kardex."""
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

        # 1. Excluir itens que não estão mais na lista (+ seu
        # movimento de kardex, para o saldo não ficar "fantasma").
        for item_id, item in itens_existentes_map.items():
            if item_id not in ids_novos:
                self.movimento_repo.excluir_por_origem(
                    session, "itens_entrada", item_id
                )
                session.delete(item)

        # 2. Atualizar existentes + inserir novos. Guardamos a
        # referência de cada item (o objeto, não o id) porque o id de
        # um item novo só é atribuído no flush logo abaixo — mas o
        # SQLAlchemy preenche item.id no próprio objeto Python após o
        # flush, então dá para usar a mesma lista depois.
        itens_para_kardex = []
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
                item = ItemEntrada(
                    entrada_id=entrada_persistida.id,
                    produto_id=item_data["produto_id"],
                    unidade=item_data["unidade"],
                    quantidade=item_data["quantidade"],
                    custo=item_data["custo"],
                )
                session.add(item)
            itens_para_kardex.append(item)

        session.flush()
        session.refresh(entrada_persistida)

        # 3. Sincronizar o kardex com o estado final dos itens desta
        # entrada (agora com item.id garantido para todos, inclusive
        # os recém-inseridos).
        for item in itens_para_kardex:
            self.movimento_repo.registrar_ou_atualizar(
                session,
                origem_tabela="itens_entrada",
                origem_id=item.id,
                produto_id=item.produto_id,
                quantidade=float(item.quantidade),
                custo_unitario=float(item.custo),
                data_movimento=entrada_persistida.data_entrada,
                tipo=TIPO_ENTRADA,
            )

        if expunge:
            session.expunge(entrada_persistida)
        return entrada_persistida

    def excluir_por_id(self, entrada_id):
        from app.repositories.consumo_producao_repository import (
            ConsumoProducaoRepository,
        )

        with session_scope() as session:
            entrada = session.query(Entrada).filter_by(id=entrada_id).first()
            if not entrada:
                return False

            # NOVO: remove os consumos de produção + seus movimentos de
            # kardex ANTES do cascade apagar a entrada — os consumos têm
            # FK para entradas e são a origem (origem_id) dos movimentos
            # de tipo CONSUMO_PRODUCAO. Sem isso, a exclusão de uma
            # entrada de produção deixaria movimentos órfãos no kardex.
            ConsumoProducaoRepository().excluir_por_entrada(
                session, entrada_id
            )

            # Remove os movimentos de kardex de cada item ANTES do
            # cascade delete apagar os itens — senão perderíamos a
            # referência (origem_id) para localizá-los.
            itens = (
                session.query(ItemEntrada)
                .filter_by(entrada_id=entrada_id)
                .all()
            )
            for item in itens:
                self.movimento_repo.excluir_por_origem(
                    session, "itens_entrada", item.id
                )

            session.delete(entrada)
            return True
