import re

from sqlalchemy.exc import IntegrityError

from app.models.saida import Saida
from app.repositories.saida_repository import SaidaRepository
from app.utils.logger import get_logger

logger = get_logger("saida_service")


class SaidaService:
    def __init__(self):
        self.repo = SaidaRepository()

    def listar_todos(self):
        return self.repo.listar_todos()

    def buscar_por_id(self, saida_id):
        return self.repo.buscar_por_id(saida_id)

    def buscar_por_sequencia(self, sequencia):
        return self.repo.buscar_por_sequencia(sequencia)

    def buscar_com_itens(self, saida_id):
        return self.repo.buscar_com_itens(saida_id)

    def obter_proxima_sequencia(self):
        return self.repo.obter_proxima_sequencia()

    def _validar(self, sequencia, data_saida, itens):
        if not sequencia:
            raise ValueError("Sequência não gerada.")

        # A sequência é gerada automaticamente, mas o campo é editável
        # na tela (usuário pode digitar manualmente para pesquisar ou
        # forçar um valor). obter_proxima_sequencia() depende de
        # cast(sequencia, Integer) no banco, então um valor não numérico
        # quebraria a geração de sequência para todas as saídas
        # seguintes. Bloqueamos isso aqui.
        if not re.fullmatch(r"\d+", str(sequencia)):
            raise ValueError("Sequência deve conter apenas números.")

        if not data_saida:
            raise ValueError("Informe a data de saída.")

        if not itens:
            raise ValueError("Adicione pelo menos um item à saída.")

        for i, item in enumerate(itens):
            if not item.get("produto_id"):
                raise ValueError(
                    f"Item {i + 1}: produto não informado."
                )

            # Conversão e checagem de faixa em passos separados (não
            # dentro do mesmo try) para que a mensagem específica não
            # seja engolida pelo except.
            try:
                qtde = float(item.get("quantidade", 0))
            except (ValueError, TypeError):
                raise ValueError(f"Item {i + 1}: quantidade inválida.")
            if qtde <= 0:
                raise ValueError(
                    f"Item {i + 1}: quantidade deve ser maior que zero."
                )

            try:
                custo = float(item.get("custo", 0))
            except (ValueError, TypeError):
                raise ValueError(f"Item {i + 1}: custo inválido.")
            if custo < 0:
                raise ValueError(
                    f"Item {i + 1}: custo não pode ser negativo."
                )

    def salvar(self, sequencia, data_saida, itens_data, saida_id=None):
        """
        Salva saída + itens na MESMA transação. Tudo commita ou tudo
        faz rollback.
        """
        self._validar(sequencia, data_saida, itens_data)

        from app.database.connection import session_scope

        try:
            with session_scope() as session:
                if saida_id:
                    saida = session.get(Saida, saida_id)
                    if not saida:
                        raise ValueError(
                            "Saída não encontrada para edição."
                        )
                    saida.sequencia = sequencia
                    saida.data_saida = data_saida
                else:
                    saida = Saida(
                        sequencia=sequencia,
                        data_saida=data_saida,
                    )
                    session.add(saida)

                session.flush()

                # Salvar itens com diff (mesma sessão). Reatribuímos
                # `saida` ao valor retornado (em vez de continuar
                # usando a referência antiga) para não depender de
                # detalhe interno do SQLAlchemy sobre session.merge()
                # retornar ou não a mesma instância.
                saida = self.repo.salvar_com_itens(
                    saida, itens_data, session=session
                )

                session.flush()
                session.refresh(saida)
                session.expunge(saida)

                logger.info(
                    f"Saída salva (transação única): ID={saida.id}, "
                    f"sequencia={saida.sequencia}, "
                    f"itens={len(itens_data)}"
                )
                return saida
        except IntegrityError:
            logger.warning(
                f"Conflito de integridade ao salvar saída "
                f"(provável sequência duplicada concorrente): {sequencia}"
            )
            raise ValueError(
                "Já existe uma saída com esta sequência. "
                "Tente novamente."
            )
        # ValueError e outras exceções sobem naturalmente;
        # session_scope() já garante o rollback de tudo.

    def excluir(self, saida_id):
        sucesso = self.repo.excluir_por_id(saida_id)
        if not sucesso:
            raise ValueError("Saída não encontrada.")
        logger.info(f"Saída excluída: ID={saida_id}")
        return True
