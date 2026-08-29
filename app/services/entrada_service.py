from app.models.entrada import Entrada
from app.repositories.entrada_repository import EntradaRepository
from app.utils.logger import get_logger

logger = get_logger("entrada_service")


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

        resultado = self.repo.salvar_com_itens(entrada, itens_data)

        logger.info(
            f"Entrada salva: ID={resultado.id}, "
            f"sequencia={resultado.sequencia}, "
            f"itens={len(itens_data)}"
        )
        return resultado

    def excluir(self, entrada_id):
        sucesso = self.repo.excluir_por_id(entrada_id)
        if not sucesso:
            raise ValueError("Entrada não encontrada.")
        logger.info(f"Entrada excluída: ID={entrada_id}")
        return True
