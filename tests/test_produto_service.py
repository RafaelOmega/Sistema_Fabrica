"""Testes da camada de service de Produto, focados nos dois campos
novos: mao_obra e controla_estoque."""
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.services.produto_service import ProdutoService


@pytest.fixture
def service():
    svc = ProdutoService()
    svc.repo = MagicMock()
    return svc


class TestSalvarComNovosCampos:
    def test_novo_produto_grava_mao_obra_e_controla_estoque(self, service):
        service.repo.buscar_por_codigo.return_value = None
        service.repo.salvar.side_effect = lambda produto: produto

        resultado = service.salvar(
            codigo="1",
            descricao="Serviço de mistura",
            peso=0,
            custo=Decimal("10.00"),
            mao_obra=True,
            controla_estoque=False,
        )

        assert resultado.mao_obra is True
        assert resultado.controla_estoque is False

    def test_valores_padrao_sao_false_quando_nao_informados(self, service):
        service.repo.buscar_por_codigo.return_value = None
        service.repo.salvar.side_effect = lambda produto: produto

        resultado = service.salvar(
            codigo="1", descricao="Produto qualquer",
            peso=1, custo=Decimal("1.00"),
        )

        assert resultado.mao_obra is False
        assert resultado.controla_estoque is False

    def test_edicao_atualiza_mao_obra_e_controla_estoque(self, service):
        produto_existente = MagicMock(
            mao_obra=False, controla_estoque=False
        )
        service.repo.buscar_por_id.return_value = produto_existente
        service.repo.salvar.side_effect = lambda produto: produto

        resultado = service.salvar(
            codigo="1", descricao="Produto X",
            peso=1, custo=Decimal("1.00"),
            produto_id=1,
            mao_obra=True,
            controla_estoque=True,
        )

        assert resultado.mao_obra is True
        assert resultado.controla_estoque is True
