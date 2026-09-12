"""
Testes da camada de service de Ficha Técnica.

Cobre principalmente a validação de `sacos_batida`, que deve ser
sempre um inteiro positivo (a coluna no banco é Integer — não existe
meio saco). O bug original permitia que a tela aceitasse valores
decimais (ex.: "1,5") no cálculo em tempo real por engano; aqui
garantimos que o service — a última linha de defesa antes de gravar —
continua rejeitando qualquer coisa que não seja um inteiro.
"""
from unittest.mock import MagicMock

import pytest

from app.services.ficha_tecnica_service import FichaTecnicaService

ITEM_VALIDO = {
    "produto_id": 2,
    "codigo_produto": "9999",
    "quantidade_kg": 10.0,
}


@pytest.fixture
def service():
    svc = FichaTecnicaService()
    svc.repo = MagicMock()
    return svc


class TestValidar:
    def test_produto_nao_selecionado(self, service):
        with pytest.raises(ValueError, match="Selecione um produto"):
            service._validar(None, "123", "10", [ITEM_VALIDO])

    def test_codigo_produto_ausente(self, service):
        with pytest.raises(ValueError, match="Código do produto"):
            service._validar(1, "", "10", [ITEM_VALIDO])

    def test_sacos_batida_vazio(self, service):
        with pytest.raises(ValueError, match="sacos por batida"):
            service._validar(1, "123", "", [ITEM_VALIDO])

    def test_sacos_batida_zero_ou_negativo(self, service):
        with pytest.raises(ValueError, match="maior que zero"):
            service._validar(1, "123", "0", [ITEM_VALIDO])

    @pytest.mark.parametrize("valor", ["1,5", "1.5", "abc", "1,5,3"])
    def test_sacos_batida_decimal_ou_invalido_e_rejeitado(
        self, service, valor
    ):
        """
        A coluna fichas_tecnicas.sacos_batida é Integer no banco.
        Um valor decimal (que a tela antes aceitava no cálculo em
        tempo real) tem que ser rejeitado aqui.
        """
        with pytest.raises(ValueError, match="Sacos por batida inválido"):
            service._validar(1, "123", valor, [ITEM_VALIDO])

    @pytest.mark.parametrize("valor", ["1", "10", "007"])
    def test_sacos_batida_inteiro_e_aceito(self, service, valor):
        service._validar(1, "123", valor, [ITEM_VALIDO])

    def test_sem_itens(self, service):
        with pytest.raises(ValueError, match="pelo menos uma matéria"):
            service._validar(1, "123", "10", [])

    def test_item_sem_materia_prima(self, service):
        item = {**ITEM_VALIDO, "produto_id": None}
        with pytest.raises(ValueError, match="matéria prima não informada"):
            service._validar(1, "123", "10", [item])

    def test_item_quantidade_invalida(self, service):
        item = {**ITEM_VALIDO, "quantidade_kg": 0}
        with pytest.raises(ValueError, match="quantidade deve ser maior"):
            service._validar(1, "123", "10", [item])


class TestSalvar:
    def test_salvar_produto_ja_tem_ficha_falha(self, service):
        service.repo.buscar_por_produto.return_value = MagicMock()

        with pytest.raises(ValueError, match="Já existe uma ficha"):
            service.salvar(
                produto_id=1,
                codigo_produto="123",
                sacos_batida="10",
                itens_data=[ITEM_VALIDO],
            )

    def test_salvar_grava_sacos_batida_como_inteiro(self, service):
        service.repo.buscar_por_produto.return_value = None
        service.repo.salvar_com_itens.side_effect = lambda ficha, itens: ficha

        resultado = service.salvar(
            produto_id=1,
            codigo_produto="123",
            sacos_batida="10",
            itens_data=[ITEM_VALIDO],
        )

        assert resultado.sacos_batida == 10
        assert isinstance(resultado.sacos_batida, int)

    def test_salvar_edicao_ficha_inexistente_falha(self, service):
        service.repo.buscar_por_id.return_value = None

        with pytest.raises(ValueError, match="não encontrada para edição"):
            service.salvar(
                produto_id=1,
                codigo_produto="123",
                sacos_batida="10",
                itens_data=[ITEM_VALIDO],
                ficha_id=999,
            )


class TestExcluir:
    def test_excluir_inexistente_falha(self, service):
        service.repo.excluir_por_id.return_value = False

        with pytest.raises(ValueError, match="não encontrada"):
            service.excluir(999)
