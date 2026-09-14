"""Testes da camada de service de Estoque."""
from datetime import date
from unittest.mock import MagicMock

import pytest

from app.services.estoque_service import EstoqueService


@pytest.fixture
def service():
    svc = EstoqueService()
    svc.repo = MagicMock()
    return svc


class TestListarSaldo:
    def test_sem_data_falha(self, service):
        with pytest.raises(ValueError, match="Informe a data"):
            service.listar_saldo(None)

    def test_repassa_parametros_para_o_repositorio(self, service):
        service.repo.listar_saldo.return_value = []
        data_limite = date(2026, 9, 12)

        service.listar_saldo(data_limite, ocultar_zerados=True)

        service.repo.listar_saldo.assert_called_once_with(
            data_limite=data_limite, ocultar_zerados=True
        )

    def test_retorna_o_que_o_repositorio_devolve(self, service):
        esperado = [{"codigo": "1", "saldo": 10.0}]
        service.repo.listar_saldo.return_value = esperado

        resultado = service.listar_saldo(date(2026, 9, 12))

        assert resultado == esperado
