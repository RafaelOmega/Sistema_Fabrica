from app.models.ficha_tecnica import FichaTecnica
from app.repositories.ficha_tecnica_repository import FichaTecnicaRepository
from app.utils.logger import get_logger

logger = get_logger("ficha_tecnica_service")


class FichaTecnicaService:
    def __init__(self):
        self.repo = FichaTecnicaRepository()

    def listar_todos(self):
        return self.repo.listar_todos()

    def buscar_por_id(self, ficha_id):
        return self.repo.buscar_por_id(ficha_id)

    def buscar_por_produto(self, produto_id):
        return self.repo.buscar_por_produto(produto_id)

    def buscar_com_itens(self, ficha_id):
        return self.repo.buscar_com_itens(ficha_id)

    def _validar(self, produto_id, codigo_produto, sacos_batida, itens):
        if not produto_id:
            raise ValueError("Selecione um produto acabado.")

        if not codigo_produto:
            raise ValueError("Código do produto não informado.")

        if not sacos_batida:
            raise ValueError("Informe a quantidade de sacos por batida.")

        # Conversão e checagem de faixa em passos separados (ver
        # explicação equivalente em EntradaService._validar) para que
        # a mensagem específica não seja engolida pelo except.
        try:
            sacos = int(sacos_batida)
        except (ValueError, TypeError):
            raise ValueError("Sacos por batida inválido.")
        if sacos <= 0:
            raise ValueError("Sacos por batida deve ser maior que zero.")

        if not itens:
            raise ValueError(
                "Adicione pelo menos uma matéria prima à ficha."
            )

        for i, item in enumerate(itens):
            if not item.get("produto_id"):
                raise ValueError(
                    f"Item {i + 1}: matéria prima não informada."
                )
            if not item.get("codigo_produto"):
                raise ValueError(
                    f"Item {i + 1}: código do produto não informado."
                )
            try:
                qtde = float(item.get("quantidade_kg", 0))
            except (ValueError, TypeError):
                raise ValueError(f"Item {i + 1}: quantidade inválida.")
            if qtde <= 0:
                raise ValueError(
                    f"Item {i + 1}: quantidade deve ser maior que zero."
                )

    def salvar(self, produto_id, codigo_produto, sacos_batida, itens_data,
               ficha_id=None):
        self._validar(produto_id, codigo_produto, sacos_batida, itens_data)

        if ficha_id is None:
            existente = self.repo.buscar_por_produto(produto_id)
            if existente:
                raise ValueError(
                    "Já existe uma ficha técnica para este produto."
                )
            ficha = FichaTecnica()
            ficha.produto_id = produto_id
            ficha.codigo_produto = codigo_produto  # ← ADICIONADO
        else:
            ficha = self.repo.buscar_por_id(ficha_id)
            if not ficha:
                raise ValueError(
                    "Ficha técnica não encontrada para edição."
                )
            ficha.codigo_produto = codigo_produto  # ← ADICIONADO (atualiza)

        ficha.sacos_batida = int(sacos_batida)

        resultado = self.repo.salvar_com_itens(ficha, itens_data)

        logger.info(
            f"Ficha técnica salva: ID={resultado.id}, "
            f"produto_id={produto_id}, codigo={codigo_produto}, "
            f"itens={len(itens_data)}"
        )
        return resultado

    def excluir(self, ficha_id):
        sucesso = self.repo.excluir_por_id(ficha_id)
        if not sucesso:
            raise ValueError("Ficha técnica não encontrada.")
        logger.info(f"Ficha técnica excluída: ID={ficha_id}")
        return True
