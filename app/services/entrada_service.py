from sqlalchemy.exc import IntegrityError

from app.models.entrada import Entrada
from app.repositories.entrada_repository import EntradaRepository
from app.utils.logger import get_logger

logger = get_logger("entrada_service")

# Configuração de regras especiais por código de produto
# Para adicionar novos produtos, basta inserir uma entrada aqui
REGRAS_PRODUTOS_ESPECIAIS = {
    "116431": {
        "descricao": "Milho 60KG",
        "divisor_custo": 60,
    },
}


class EntradaService:
    def __init__(self):
        self.repo = EntradaRepository()

    def listar_todos(self):
        return self.repo.listar_todos()

    def buscar_por_id(self, entrada_id):
        return self.repo.buscar_por_id(entrada_id)

    def buscar_por_sequencia(self, sequencia):
        return self.repo.buscar_por_sequencia(sequencia)

    def buscar_com_itens(self, entrada_id):
        return self.repo.buscar_com_itens(entrada_id)

    def obter_proxima_sequencia(self):
        return self.repo.obter_proxima_sequencia()

    def obter_regra_produto(self, codigo_produto):
        """Retorna a regra especial do produto, ou None se não houver."""
        return REGRAS_PRODUTOS_ESPECIAIS.get(str(codigo_produto))

    def _validar(self, sequencia, data_entrada, motivo_id, itens):
        if not sequencia:
            raise ValueError("Sequência não gerada.")

        if not data_entrada:
            raise ValueError("Informe a data de entrada.")

        if not motivo_id:
            raise ValueError("Selecione um motivo de entrada.")

        if not itens:
            raise ValueError("Adicione pelo menos um item à entrada.")

        for i, item in enumerate(itens):
            if not item.get("produto_id"):
                raise ValueError(
                    f"Item {i + 1}: produto não informado."
                )
            if not item.get("unidade"):
                raise ValueError(
                    f"Item {i + 1}: unidade não informada."
                )
            try:
                qtde = float(item.get("quantidade", 0))
                if qtde <= 0:
                    raise ValueError(
                        f"Item {i + 1}: quantidade deve ser maior que zero."
                    )
            except (ValueError, TypeError):
                raise ValueError(f"Item {i + 1}: quantidade inválida.")
            try:
                custo = float(item.get("custo", 0))
                if custo < 0:
                    raise ValueError(
                        f"Item {i + 1}: custo não pode ser negativo."
                    )
            except (ValueError, TypeError):
                raise ValueError(f"Item {i + 1}: custo inválido.")

    def salvar(self, sequencia, data_entrada, motivo_id, itens_data,
               entrada_id=None):
        self._validar(sequencia, data_entrada, motivo_id, itens_data)

        if entrada_id is None:
            entrada = Entrada()
            entrada.sequencia = sequencia
        else:
            entrada = self.repo.buscar_por_id(entrada_id)
            if not entrada:
                raise ValueError("Entrada não encontrada para edição.")

        entrada.data_entrada = data_entrada
        entrada.motivo_entrada_id = motivo_id

        try:
            resultado = self.repo.salvar_com_itens(entrada, itens_data)
        except IntegrityError:
            logger.warning(
                f"Conflito de integridade ao salvar entrada "
                f"(provável sequência duplicada concorrente): {sequencia}"
            )
            raise ValueError(
                "Já existe uma entrada com esta sequência. "
                "Tente novamente."
            )

        logger.info(
            f"Entrada salva: ID={resultado.id}, "
            f"sequencia={resultado.sequencia}, "
            f"itens={len(itens_data)}"
        )
        return resultado

    def salvar_com_alteracao_custo(self, sequencia, data_entrada, motivo_id,
                                   itens_data, entrada_id=None,
                                   alteracoes_custo=None):
        """
        Salva entrada + itens + alterações de custo na MESMA transação.
        Tudo commita ou tudo faz rollback.
        """
        self._validar(sequencia, data_entrada, motivo_id, itens_data)

        from app.database.connection import session_scope
        from app.repositories.alteracao_custo_repository import (
            AlteracaoCustoRepository,
        )
        from app.repositories.produto_repository import ProdutoRepository

        alteracao_repo = AlteracaoCustoRepository()
        produto_repo = ProdutoRepository()

        try:
            with session_scope() as session:
                # 1. Build/save entrada
                if entrada_id:
                    from app.models.entrada import Entrada as EntradaModel
                    entrada = session.query(EntradaModel).get(entrada_id)
                    if not entrada:
                        raise ValueError(
                            "Entrada não encontrada para edição."
                        )
                    entrada.sequencia = sequencia
                    entrada.data_entrada = data_entrada
                    entrada.motivo_entrada_id = motivo_id
                else:
                    entrada = Entrada(
                        sequencia=sequencia,
                        data_entrada=data_entrada,
                        motivo_entrada_id=motivo_id,
                    )
                    session.add(entrada)

                session.flush()

                # 2. Salvar itens com diff (mesma sessão)
                self.repo.salvar_com_itens(
                    entrada, itens_data, session=session
                )

                # 3. Salvar alterações de custo + atualizar produto
                if alteracoes_custo:
                    for alt in alteracoes_custo:
                        alteracao_repo.registrar(
                            codigo_produto=alt["codigo_produto"],
                            custo_anterior=alt["custo_anterior"],
                            custo_atual=alt["custo_atual"],
                            session=session,
                        )
                        produto_repo.atualizar_custo(
                            produto_id=alt["produto_id"],
                            novo_custo=alt["custo_atual"],
                            session=session,
                        )

                session.flush()
                session.refresh(entrada)
                session.expunge(entrada)

                logger.info(
                    f"Entrada salva (transação única): ID={entrada.id}, "
                    f"sequencia={entrada.sequencia}, "
                    f"itens={len(itens_data)}"
                )
                return entrada
        except IntegrityError:
            logger.warning(
                f"Conflito de integridade ao salvar entrada "
                f"(provável sequência duplicada concorrente): {sequencia}"
            )
            raise ValueError(
                "Já existe uma entrada com esta sequência. "
                "Tente novamente."
            )
        # ValueError e outras exceções sobem naturalmente;
        # session_scope() já garante o rollback de tudo.

    def excluir(self, entrada_id):
        sucesso = self.repo.excluir_por_id(entrada_id)
        if not sucesso:
            raise ValueError("Entrada não encontrada.")
        logger.info(f"Entrada excluída: ID={entrada_id}")
        return True
