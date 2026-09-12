"""
Testes da camada de service de Entrada de Mercadorias.

Assim como em test_motivo_entrada_service.py, substituímos os
repositórios reais (self.repo, self.regra_repo) por MagicMock após a
construção do service, para testar só a lógica de negócio sem
depender de um banco Postgres real.

O método `salvar()` faz imports locais de `session_scope`,
`AlteracaoCustoRepository` e `ProdutoRepository` dentro do próprio
método (para manter a transação isolada) — por isso o teste do fluxo
completo usa monkeypatch nesses pontos de import.
"""
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.services.entrada_service import EntradaService

ITEM_VALIDO = {
    "produto_id": 1,
    "unidade": "UN",
    "quantidade": 10,
    "custo": 5.0,
}


@pytest.fixture
def service():
    svc = EntradaService()
    svc.repo = MagicMock()
    svc.regra_repo = MagicMock()
    svc.regra_repo.listar_todos.return_value = []
    return svc


class TestValidar:
    def test_sequencia_vazia(self, service):
        with pytest.raises(ValueError, match="Sequência não gerada"):
            service._validar("", "2026-01-01", 1, [ITEM_VALIDO])

    @pytest.mark.parametrize("sequencia", ["ABC", "1A", "1.5", "1,5", "-1"])
    def test_sequencia_nao_numerica_e_rejeitada(self, service, sequencia):
        """
        obter_proxima_sequencia() usa cast(sequencia, Integer) no banco.
        O campo é editável na tela, então uma sequência digitada
        manualmente com letras quebraria a geração de próxima
        sequência para todas as entradas seguintes.
        """
        with pytest.raises(ValueError, match="apenas números"):
            service._validar(sequencia, "2026-01-01", 1, [ITEM_VALIDO])

    def test_sequencia_numerica_e_aceita(self, service):
        service._validar("42", "2026-01-01", 1, [ITEM_VALIDO])

    def test_data_entrada_vazia(self, service):
        with pytest.raises(ValueError, match="Informe a data de entrada"):
            service._validar("1", "", 1, [ITEM_VALIDO])

    def test_motivo_nao_selecionado(self, service):
        with pytest.raises(ValueError, match="Selecione um motivo"):
            service._validar("1", "2026-01-01", None, [ITEM_VALIDO])

    def test_sem_itens(self, service):
        with pytest.raises(ValueError, match="pelo menos um item"):
            service._validar("1", "2026-01-01", 1, [])

    def test_item_sem_produto(self, service):
        item = {**ITEM_VALIDO, "produto_id": None}
        with pytest.raises(ValueError, match="produto não informado"):
            service._validar("1", "2026-01-01", 1, [item])

    def test_item_sem_unidade(self, service):
        item = {**ITEM_VALIDO, "unidade": ""}
        with pytest.raises(ValueError, match="unidade não informada"):
            service._validar("1", "2026-01-01", 1, [item])

    def test_item_quantidade_zero(self, service):
        item = {**ITEM_VALIDO, "quantidade": 0}
        with pytest.raises(ValueError, match="maior que zero"):
            service._validar("1", "2026-01-01", 1, [item])

    def test_item_custo_negativo(self, service):
        item = {**ITEM_VALIDO, "custo": -1}
        with pytest.raises(ValueError, match="não pode ser negativo"):
            service._validar("1", "2026-01-01", 1, [item])


class TestRegraProdutoEspecial:
    def test_sem_regra_cadastrada_retorna_none(self, service):
        assert service.obter_regra_produto("999999") is None

    def test_regra_vem_do_banco_e_e_cacheada(self, service):
        service.regra_repo.listar_todos.return_value = [
            SimpleNamespace(
                codigo_produto="116431",
                descricao="Milho 60KG",
                divisor_custo=60,
            )
        ]

        regra = service.obter_regra_produto("116431")
        assert regra == {"descricao": "Milho 60KG", "divisor_custo": 60.0}

        # Segunda chamada não deve ir ao banco de novo (cache em memória).
        service.regra_repo.listar_todos.reset_mock()
        service.obter_regra_produto("116431")
        service.regra_repo.listar_todos.assert_not_called()

    def test_invalidar_cache_forca_releitura(self, service):
        service.regra_repo.listar_todos.return_value = []
        service.obter_regra_produto("116431")

        service.invalidar_cache_regras()
        service.regra_repo.listar_todos.reset_mock()
        service.obter_regra_produto("116431")
        service.regra_repo.listar_todos.assert_called_once()

    def test_salvar_regra_com_divisor_invalido_falha(self, service):
        with pytest.raises(ValueError, match="Divisor de custo inválido"):
            service.salvar_regra_produto_especial(
                codigo_produto="123", descricao="Teste", divisor_custo="abc"
            )

    def test_salvar_regra_com_sucesso_invalida_cache(self, service):
        service.regra_repo.salvar.return_value = MagicMock()
        service.obter_regra_produto("116431")  # popula cache (vazio)

        service.salvar_regra_produto_especial(
            codigo_produto="116431", descricao="Milho 60KG", divisor_custo=60
        )

        assert service._cache_regras is None  # cache invalidado


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

        with pytest.raises(ValueError, match="Já existe uma entrada"):
            service.salvar(
                sequencia="1",
                data_entrada="2026-01-01",
                motivo_id=1,
                itens_data=[ITEM_VALIDO],
            )

    def test_salvar_happy_path_e_transacional(self, service, monkeypatch):
        fake_session = MagicMock()
        fake_session.get.return_value = None  # força criar Entrada nova

        @contextmanager
        def fake_session_scope():
            yield fake_session

        monkeypatch.setattr(
            "app.database.connection.session_scope", fake_session_scope
        )
        monkeypatch.setattr(
            "app.repositories.alteracao_custo_repository."
            "AlteracaoCustoRepository",
            lambda: MagicMock(),
        )
        monkeypatch.setattr(
            "app.repositories.produto_repository.ProdutoRepository",
            lambda: MagicMock(),
        )
        # Simula o comportamento real: salvar_com_itens retorna a
        # própria entrada recebida (persistida/atualizada), já que
        # EntradaService.salvar agora reatribui `entrada` a esse
        # retorno em vez de confiar na referência original.
        service.repo.salvar_com_itens.side_effect = (
            lambda entrada, itens_data, session: entrada
        )

        entrada = service.salvar(
            sequencia="1",
            data_entrada="2026-01-01",
            motivo_id=1,
            itens_data=[ITEM_VALIDO],
        )

        assert entrada.sequencia == "1"
        assert entrada.motivo_entrada_id == 1
        service.repo.salvar_com_itens.assert_called_once()
        fake_session.add.assert_called_once_with(entrada)

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
                data_entrada="2026-01-01",
                motivo_id=1,
                itens_data=[ITEM_VALIDO],
            )

        session_scope_mock.assert_not_called()
