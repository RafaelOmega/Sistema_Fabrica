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

        if not data_saida:
            raise ValueError("Informe a data de saída.")

        if not itens:
            raise ValueError("Adicione pelo menos um item à saída.")

        for i, item in enumerate(itens):
            if not item.get("produto_id"):
                raise ValueError(
                    f"Item {i + 1}: produto não informado."
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

    def salvar(self, sequencia, data_saida, itens_data, saida_id=None):
        """
        Salva saída + itens em transação única.
        Tudo commita ou tudo faz rollback.
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

                # salvar_com_itens já faz merge + flush + refresh + expunge
                # e retorna a instância persistida (desanexada)
                saida_salva = self.repo.salvar_com_itens(
                    saida, itens_data, session=session
                )

                logger.info(
                    f"Saída salva (transação única): ID={saida_salva.id}, "
                    f"sequencia={saida_salva.sequencia}, "
                    f"itens={len(itens_data)}"
                )
                return saida_salva
        except IntegrityError:
            logger.warning(
                f"Conflito de integridade ao salvar saída "
                f"(provável sequência duplicada concorrente): {sequencia}"
            )
            raise ValueError(
                "Já existe uma saída com esta sequência. "
                "Tente novamente."
            )

    def excluir(self, saida_id):
        sucesso = self.repo.excluir_por_id(saida_id)
        if not sucesso:
            raise ValueError("Saída não encontrada.")
        logger.info(f"Saída excluída: ID={saida_id}")
        return True
