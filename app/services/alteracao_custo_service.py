from app.repositories.alteracao_custo_repository import AlteracaoCustoRepository
from app.utils.logger import get_logger

logger = get_logger("alteracao_custo_service")


class AlteracaoCustoService:
    def __init__(self):
        self.repo = AlteracaoCustoRepository()

    def registrar_alteracao(self, codigo_produto, custo_anterior, custo_atual):
        if custo_anterior == custo_atual:
            return None

        registro = self.repo.registrar(
            codigo_produto=codigo_produto,
            custo_anterior=custo_anterior,
            custo_atual=custo_atual,
        )
        logger.info(
            f"Custo alterado | produto={codigo_produto} | "
            f"de {custo_anterior} para {custo_atual}"
        )
        return registro
