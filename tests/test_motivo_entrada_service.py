"""
Testes da camada de service de Motivo de Entrada.

O service instancia seu próprio repositório em __init__
(self.repo = MotivoEntradaRepository()), então aqui trocamos
`service.repo` por um MagicMock após a construção, em vez de acessar
o banco de verdade. Isso testa apenas a lógica de negócio/validação,
que é o que realmente precisa de cobertura de teste.
"""
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.services.motivo_entrada_service import MotivoEntradaService


@pytest.fixture
def service():
    svc = MotivoEntradaService()
    svc.repo = MagicMock()
    return svc


class TestValidar:
    def test_codigo_vazio(self, service):
        with pytest.raises(ValueError, match="Preencha código e descrição"):
            service._validar("", "Compra de insumos")

    def test_descricao_vazia(self, service):
        with pytest.raises(ValueError, match="Preencha código e descrição"):
            service._validar("1", "")

    def test_codigo_muito_longo(self, service):
        with pytest.raises(ValueError, match="máximo 50 caracteres"):
            service._validar("1" * 51, "Descrição válida")

    def test_descricao_muito_longa(self, service):
        with pytest.raises(ValueError, match="máximo 255 caracteres"):
            service._validar("1", "x" * 256)

    @pytest.mark.parametrize("codigo", ["ABC", "12A", "1.5", "1,5", "-1", " "])
    def test_codigo_nao_numerico_e_rejeitado(self, service, codigo):
        """
        obter_proximo_codigo() usa cast(codigo, Integer) no banco.
        Um código não numérico quebraria a geração de próximo código
        para todos os registros seguintes, então deve ser rejeitado
        na validação.
        """
        with pytest.raises(ValueError, match="apenas números"):
            service._validar(codigo, "Descrição válida")

    @pytest.mark.parametrize("codigo", ["1", "007", "12345"])
    def test_codigo_numerico_e_aceito(self, service, codigo):
        # Não deve levantar exceção.
        service._validar(codigo, "Descrição válida")


class TestSalvar:
    def test_salvar_novo_com_codigo_duplicado_falha(self, service):
        service.repo.buscar_por_codigo.return_value = MagicMock()  # já existe

        with pytest.raises(ValueError, match="[Jj]á existe um motivo"):
            service.salvar(codigo="1", descricao="Compra")

    def test_salvar_novo_com_sucesso(self, service):
        service.repo.buscar_por_codigo.return_value = None
        esperado = MagicMock(id=1, codigo="1", descricao="Compra")
        service.repo.salvar.return_value = esperado

        resultado = service.salvar(codigo="1", descricao="Compra")

        assert resultado is esperado
        service.repo.salvar.assert_called_once()

    def test_salvar_edicao_motivo_inexistente_falha(self, service):
        service.repo.buscar_por_id.return_value = None

        with pytest.raises(ValueError, match="não encontrado para edição"):
            service.salvar(codigo="1", descricao="Compra", motivo_id=999)

    def test_conflito_integridade_vira_value_error_amigavel(self, service):
        service.repo.buscar_por_codigo.return_value = None
        service.repo.salvar.side_effect = IntegrityError(
            "stmt", {}, Exception("duplicate key")
        )

        with pytest.raises(ValueError, match="[Jj]á existe um motivo"):
            service.salvar(codigo="1", descricao="Compra")

    def test_codigo_e_descricao_sao_normalizados_com_strip(self, service):
        service.repo.buscar_por_codigo.return_value = None
        service.repo.salvar.side_effect = lambda motivo: motivo

        service.salvar(codigo="  1  ", descricao="  Compra  ")

        motivo_passado = service.repo.salvar.call_args[0][0]
        assert motivo_passado.codigo == "1"
        assert motivo_passado.descricao == "Compra"


class TestExcluir:
    def test_excluir_inexistente_falha(self, service):
        service.repo.excluir_por_id.return_value = False

        with pytest.raises(ValueError, match="não encontrado"):
            service.excluir(999)

    def test_excluir_com_sucesso(self, service):
        service.repo.excluir_por_id.return_value = True

        assert service.excluir(1) is True
