"""
Testes da camada de service de Saída de Mercadorias.

Mesmo padrão de test_entrada_service.py: `service.repo` é substituído
por MagicMock para testar apenas a lógica de negócio/validação.
"""
from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.services.saida_service import SaidaService

ITEM_VALIDO = {
    "produto_id": 1,
    "quantidade": 10,
    "custo": 5.0,
}


@pytest.fixture
def service():
    svc = SaidaService()
    svc.repo = MagicMock()
    return svc


class TestValidar:
    def test_sequencia_vazia(self, service):
        with pytest.raises(ValueError, match="Sequência não gerada"):
            service._validar("", "2026-01-01", [ITEM_VALIDO])

    @pytest.mark.parametrize("sequencia", ["ABC", "1A", "1.5", "1,5", "-1"])
    def test_sequencia_nao_numerica_e_rejeitada(self, service, sequencia):
        with pytest.raises(ValueError, match="apenas números"):
            service._validar(sequencia, "2026-01-01", [ITEM_VALIDO])

    def test_sequencia_numerica_e_aceita(self, service):
        service._validar("42", "2026-01-01", [ITEM_VALIDO])

    def test_data_saida_vazia(self, service):
        with pytest.raises(ValueError, match="Informe a data de saída"):
            service._validar("1", "", [ITEM_VALIDO])

    def test_sem_itens(self, service):
        with pytest.raises(ValueError, match="pelo menos um item"):
            service._validar("1", "2026-01-01", [])

    def test_item_sem_produto(self, service):
        item = {**ITEM_VALIDO, "produto_id": None}
        with pytest.raises(ValueError, match="produto não informado"):
            service._validar("1", "2026-01-01", [item])

    def test_item_quantidade_zero(self, service):
        item = {**ITEM_VALIDO, "quantidade": 0}
        with pytest.raises(ValueError, match="maior que zero"):
            service._validar("1", "2026-01-01", [item])

    def test_item_quantidade_invalida(self, service):
        item = {**ITEM_VALIDO, "quantidade": "abc"}
        with pytest.raises(ValueError, match="quantidade inválida"):
            service._validar("1", "2026-01-01", [item])

    def test_item_custo_negativo(self, service):
        item = {**ITEM_VALIDO, "custo": -1}
        with pytest.raises(ValueError, match="não pode ser negativo"):
            service._validar("1", "2026-01-01", [item])

    def test_item_custo_invalido(self, service):
        item = {**ITEM_VALIDO, "custo": "abc"}
        with pytest.raises(ValueError, match="custo inválido"):
            service._validar("1", "2026-01-01", [item])


class TestSalvarTransacional:
    def test_conflito_de_sequencia_vira_value_error_amigavel(
        self, service, monkeypatch
    ):
        @contextmanager
        def fake_session_scope():
            session = MagicMock()
            session.get.return_value = None
            yield session

        monkeypatch.setattr(
            "app.database.connection.session_scope", fake_session_scope
        )
        service.repo.salvar_com_itens.side_effect = IntegrityError(
            "stmt", {}, Exception("duplicate key")
        )

        with pytest.raises(ValueError, match="Já existe uma saída"):
            service.salvar(
                sequencia="1",
                data_saida="2026-01-01",
                itens_data=[ITEM_VALIDO],
            )

    def test_salvar_happy_path_e_transacional(self, service, monkeypatch):
        fake_session = MagicMock()
        fake_session.get.return_value = None  # força criar Saida nova

        @contextmanager
        def fake_session_scope():
            yield fake_session

        monkeypatch.setattr(
            "app.database.connection.session_scope", fake_session_scope
        )
        service.repo.salvar_com_itens.side_effect = (
            lambda saida, itens_data, session: saida
        )

        saida = service.salvar(
            sequencia="1",
            data_saida="2026-01-01",
            itens_data=[ITEM_VALIDO],
        )

        assert saida.sequencia == "1"
        service.repo.salvar_com_itens.assert_called_once()
        fake_session.add.assert_called_once_with(saida)

    def test_salvar_com_sequencia_invalida_nao_chega_a_abrir_sessao(
        self, service, monkeypatch
    ):
        """A validação deve barrar ANTES de abrir qualquer transação."""
        session_scope_mock = MagicMock()
        monkeypatch.setattr(
            "app.database.connection.session_scope", session_scope_mock
        )

        with pytest.raises(ValueError, match="apenas números"):
            service.salvar(
                sequencia="ABC",
                data_saida="2026-01-01",
                itens_data=[ITEM_VALIDO],
            )

        session_scope_mock.assert_not_called()


class TestExcluir:
    def test_excluir_inexistente_falha(self, service):
        service.repo.excluir_por_id.return_value = False

        with pytest.raises(ValueError, match="não encontrada"):
            service.excluir(999)

    def test_excluir_com_sucesso(self, service):
        service.repo.excluir_por_id.return_value = True

        assert service.excluir(1) is True
