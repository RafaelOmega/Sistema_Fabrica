from app.repositories.estoque_repository import EstoqueRepository
from app.utils.logger import get_logger

logger = get_logger("estoque_service")


class EstoqueService:
    def __init__(self):
        self.repo = EstoqueRepository()

    def listar_saldo(self, data_limite, ocultar_zerados=False):
        if not data_limite:
            raise ValueError("Informe a data para calcular o saldo.")
        return self.repo.listar_saldo(
            data_limite=data_limite, ocultar_zerados=ocultar_zerados
        )
