from sqlalchemy.exc import IntegrityError

from app.models.ficha_tecnica import FichaTecnica
from app.repositories.ficha_tecnica_repository import FichaTecnicaRepository
from app.repositories.produto_repository import ProdutoRepository
from app.utils.logger import get_logger

logger = get_logger("ficha_tecnica_service")


class FichaTecnicaService:
    def __init__(self):
        self.repo = FichaTecnicaRepository()
        self.produto_repo = ProdutoRepository()

    def buscar_por_id(self, ficha_id):
        return self.repo.buscar_por_id(ficha_id)

    def buscar_por_produto_acabado(self, produto_acabado_id):
        return self.repo.buscar_por_produto_acabado_id(produto_acabado_id)

    def buscar_com_itens(self, ficha_id):
        return self.repo.buscar_com_itens(ficha_id)

    def validar_produto_acabado(self, produto):
        """Confere se um produto pode ser usado como produto acabado
        de uma ficha técnica. Levanta ValueError se não puder."""
        if produto is None:
            raise ValueError("Produto não encontrado.")
        if not getattr(produto, "prod_acabado", False):
            raise ValueError(
                f"O produto '{produto.codigo}' não está marcado "
                f"como Produto Acabado."
            )

    def validar_materia_prima(self, produto, produto_acabado_id):
        """Confere se um produto pode ser usado como matéria-prima
        de uma ficha técnica. Levanta ValueError se não puder."""
        if produto is None:
            raise ValueError("Matéria-prima não encontrada.")
        if not getattr(produto, "mat_prima", False):
            raise ValueError(
                f"O produto '{produto.codigo}' não está marcado "
                f"como Matéria-Prima."
            )
        if produto_acabado_id is not None and produto.id == produto_acabado_id:
            raise ValueError(
                "O produto acabado não pode compor a própria ficha técnica."
            )

    def _validar(self, produto_acabado_id, sacos_por_batida, itens):
        if not produto_acabado_id:
            raise ValueError("Informe o produto acabado.")

        try:
            sacos = int(sacos_por_batida)
            if sacos <= 0:
                raise ValueError(
                    "Quantidade de sacos por batida deve ser maior que zero."
                )
        except (TypeError, ValueError):
            raise ValueError("Quantidade de sacos por batida inválida.")

        if not itens:
            raise ValueError(
                "Adicione pelo menos uma matéria-prima à ficha técnica."
            )

        materias_vistas = set()
        for i, item in enumerate(itens):
            materia_id = item.get("materia_prima_id")
            if not materia_id:
                raise ValueError(
                    f"Item {i + 1}: matéria-prima não informada."
                )
            if materia_id in materias_vistas:
                raise ValueError(
                    f"Item {i + 1}: matéria-prima duplicada na ficha. "
                    f"Edite o item existente em vez de adicioná-lo de novo."
                )
            materias_vistas.add(materia_id)

            try:
                qtde = float(item.get("quantidade", 0))
                if qtde <= 0:
                    raise ValueError(
                        f"Item {i + 1}: quantidade deve ser maior que zero."
                    )
            except (ValueError, TypeError):
                raise ValueError(f"Item {i + 1}: quantidade inválida.")

    def salvar(self, produto_acabado_id, sacos_por_batida, itens_data,
               ficha_id=None):
        self._validar(produto_acabado_id, sacos_por_batida, itens_data)

        if ficha_id is None:
            existente = self.repo.buscar_por_produto_acabado_id(
                produto_acabado_id
            )
            if existente:
                logger.warning(
                    f"Ficha técnica já existe para o produto "
                    f"acabado ID={produto_acabado_id}"
                )
                raise ValueError(
                    "Já existe uma ficha técnica para este produto acabado."
                )
            ficha = FichaTecnica()
            ficha.produto_acabado_id = produto_acabado_id
        else:
            ficha = self.repo.buscar_por_id(ficha_id)
            if not ficha:
                raise ValueError("Ficha técnica não encontrada para edição.")

        ficha.sacos_por_batida = int(sacos_por_batida)

        try:
            resultado = self.repo.salvar_com_itens(ficha, itens_data)
        except IntegrityError:
            logger.warning(
                f"Conflito de integridade ao salvar ficha técnica "
                f"(provável ficha duplicada concorrente): "
                f"produto_acabado_id={produto_acabado_id}"
            )
            raise ValueError(
                "Já existe uma ficha técnica para este produto acabado."
            )

        logger.info(
            f"Ficha técnica salva: ID={resultado.id}, "
            f"produto_acabado_id={resultado.produto_acabado_id}, "
            f"itens={len(itens_data)}"
        )
        return resultado

    def excluir(self, ficha_id):
        sucesso = self.repo.excluir_por_id(ficha_id)
        if not sucesso:
            raise ValueError("Ficha técnica não encontrada.")
        logger.info(f"Ficha técnica excluída: ID={ficha_id}")
        return True
