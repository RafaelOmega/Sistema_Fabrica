from sqlalchemy.exc import IntegrityError

from app.models.produto import Produto
from app.repositories.produto_repository import ProdutoRepository
from app.utils.logger import get_logger

logger = get_logger("produto_service")


class ProdutoService:
    def __init__(self):
        self.repo = ProdutoRepository()

    def listar_todos(self):
        return self.repo.listar_todos()

    def pesquisar(self, termo):
        return self.repo.pesquisar(termo)

    def buscar_por_id(self, produto_id):
        return self.repo.buscar_por_id(produto_id)

    def buscar_por_codigo(self, codigo):
        return self.repo.buscar_por_codigo(codigo)

    def _validar(self, codigo, descricao, peso, custo):
        if not codigo or not descricao:
            raise ValueError("Preencha código e descrição.")

        if len(codigo) > 50:
            raise ValueError("Código deve ter no máximo 50 caracteres.")

        if len(descricao) > 255:
            raise ValueError("Descrição deve ter no máximo 255 caracteres.")

        if peso < 0:
            raise ValueError("Peso não pode ser negativo.")

        if custo < 0:
            raise ValueError("Custo não pode ser negativo.")

    def salvar(self, codigo, descricao, peso, custo, produto_id=None):
        codigo = codigo.strip()
        descricao = descricao.strip()

        self._validar(codigo, descricao, peso, custo)

        if produto_id is None:
            existente = self.repo.buscar_por_codigo(codigo)
            if existente:
                logger.warning(f"Código duplicado ao salvar: {codigo}")
                raise ValueError("Já existe um produto com este código.")

            produto = Produto()
        else:
            produto = self.repo.buscar_por_id(produto_id)
            if not produto:
                logger.warning(
                    f"Produto não encontrado para edição: ID={produto_id}")
                raise ValueError("Produto não encontrado para edição.")

        produto.codigo = codigo
        produto.descricao = descricao
        produto.peso = peso
        produto.custo = custo

        try:
            resultado = self.repo.salvar(produto)
        except IntegrityError:
            logger.warning(
                f"Conflito de integridade ao salvar (provável código duplicado concorrente): {codigo}"
            )
            raise ValueError("Já existe um produto com este código.")

        logger.info(
            f"Produto salvo: ID={resultado.id}, codigo={resultado.codigo}")
        return resultado

    def excluir(self, produto_id):
        sucesso = self.repo.excluir_por_id(produto_id)

        if not sucesso:
            logger.warning(
                f"Tentativa de excluir produto inexistente: ID={produto_id}")
            raise ValueError("Produto não encontrado.")

        logger.info(f"Produto excluído: ID={produto_id}")
        return True
