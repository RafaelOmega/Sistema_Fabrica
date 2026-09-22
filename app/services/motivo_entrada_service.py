import re

from sqlalchemy.exc import IntegrityError

from app.models.motivo_entrada import Motivo_Entrada
from app.repositories.motivo_entrada_repository import MotivoEntradaRepository
from app.utils.logger import get_logger

logger = get_logger("motivo_entrada_service")


class MotivoEntradaService:
    def __init__(self):
        self.repo = MotivoEntradaRepository()

    def listar_todos(self):
        return self.repo.listar_todos()

    def pesquisar(self, termo):
        return self.repo.pesquisar(termo)

    def buscar_por_id(self, motivo_id):
        return self.repo.buscar_por_id(motivo_id)

    def obter_proximo_codigo(self):
        return self.repo.obter_proximo_codigo()

    def _validar(self, codigo, descricao):
        if not codigo or not descricao:
            raise ValueError("Preencha código e descrição.")

        if len(codigo) > 50:
            raise ValueError("Código deve ter no máximo 50 caracteres.")

        # O código é gerado automaticamente (obter_proximo_codigo) usando
        # func.max(cast(codigo, Integer)) no banco. Se um código não
        # numérico entrasse aqui, a geração do próximo código passaria
        # a falhar para todos os registros seguintes. Validamos na
        # entrada para que isso nunca aconteça.
        if not re.fullmatch(r"\d+", codigo):
            raise ValueError("Código deve conter apenas números.")

        if len(descricao) > 255:
            raise ValueError("Descrição deve ter no máximo 255 caracteres.")

    def salvar(self, codigo, descricao, producao=False, motivo_id=None):
        codigo = codigo.strip()
        descricao = descricao.strip()

        self._validar(codigo, descricao)

        if motivo_id is None:
            existente = self.repo.buscar_por_codigo(codigo)
            if existente:
                logger.warning(f"Código duplicado ao salvar: {codigo}")
                raise ValueError(
                    "Já existe um motivo de entrada com este código.")

            motivo = Motivo_Entrada()
        else:
            motivo = self.repo.buscar_por_id(motivo_id)
            if not motivo:
                logger.warning(
                    f"Motivo de entrada não encontrado para edição: ID={motivo_id}")
                raise ValueError(
                    "Motivo de entrada não encontrado para edição.")

        motivo.codigo = codigo
        motivo.descricao = descricao
        # NOVO: flag de produção — entradas com este motivo dão baixa
        # automática da matéria-prima da ficha técnica e entram o
        # produto acabado no estoque.
        motivo.producao = bool(producao)

        try:
            resultado = self.repo.salvar(motivo)
        except IntegrityError:
            logger.warning(
                f"Conflito de integridade ao salvar (provável código duplicado concorrente): {codigo}"
            )
            raise ValueError("Já existe um motivo de entrada com este código.")

        logger.info(
            f"Motivo de entrada salvo: ID={resultado.id}, codigo={resultado.codigo}, "
            f"producao={resultado.producao}")
        return resultado

    def excluir(self, motivo_id):
        sucesso = self.repo.excluir_por_id(motivo_id)

        if not sucesso:
            logger.warning(
                f"Tentativa de excluir motivo de entrada inexistente: ID={motivo_id}")
            raise ValueError("Motivo de entrada não encontrado.")

        logger.info(f"Motivo de entrada excluído: ID={motivo_id}")
        return True
