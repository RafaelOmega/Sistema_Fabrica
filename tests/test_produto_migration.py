"""
Testa `_migrar_colunas_produto()` isoladamente: simula uma tabela
`produtos` "antiga" (sem as colunas mao_obra/controla_estoque) e
confirma que a migração adiciona as colunas sem apagar dados
existentes.

`app.database.connection.engine` é criado uma única vez, no import do
módulo, e amarrado à configuração real do Postgres — por isso é
substituído aqui via monkeypatch por um engine SQLite em memória
antes de chamar a função.
"""
from sqlalchemy import create_engine, text

from app.database import connection


def test_migracao_adiciona_colunas_em_tabela_antiga(monkeypatch):
    engine_teste = create_engine("sqlite:///:memory:")

    # Simula o schema ANTIGO de produtos (antes de mao_obra e
    # controla_estoque existirem), com um registro já cadastrado.
    with engine_teste.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE produtos (
                id INTEGER PRIMARY KEY,
                codigo VARCHAR(50) UNIQUE NOT NULL,
                descricao VARCHAR(255) NOT NULL,
                peso FLOAT NOT NULL DEFAULT 0,
                custo NUMERIC(10, 2) NOT NULL DEFAULT 0,
                prod_acabado BOOLEAN NOT NULL DEFAULT 0,
                mat_prima BOOLEAN NOT NULL DEFAULT 0
            )
            """
        ))
        conn.execute(text(
            "INSERT INTO produtos (codigo, descricao) "
            "VALUES ('1', 'Produto Antigo')"
        ))

    monkeypatch.setattr(connection, "engine", engine_teste)

    connection._migrar_colunas_produto()

    with engine_teste.connect() as conn:
        colunas = {
            row[1] for row in conn.execute(
                text("PRAGMA table_info(produtos)")
            )
        }
        assert "mao_obra" in colunas
        assert "controla_estoque" in colunas

        linha = conn.execute(
            text("SELECT codigo, mao_obra, controla_estoque FROM produtos")
        ).first()
        # Registro pré-existente preservado, com as colunas novas
        # assumindo o default (false) em vez de NULL.
        assert linha[0] == "1"
        assert linha[1] in (0, False)
        assert linha[2] in (0, False)


def test_migracao_e_idempotente(monkeypatch):
    """Rodar a migração duas vezes não pode falhar (ex.: reinício do
    app depois que as colunas já foram adicionadas)."""
    engine_teste = create_engine("sqlite:///:memory:")

    with engine_teste.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE produtos (
                id INTEGER PRIMARY KEY,
                codigo VARCHAR(50) UNIQUE NOT NULL,
                descricao VARCHAR(255) NOT NULL,
                peso FLOAT NOT NULL DEFAULT 0,
                custo NUMERIC(10, 2) NOT NULL DEFAULT 0,
                prod_acabado BOOLEAN NOT NULL DEFAULT 0,
                mat_prima BOOLEAN NOT NULL DEFAULT 0
            )
            """
        ))

    monkeypatch.setattr(connection, "engine", engine_teste)

    connection._migrar_colunas_produto()
    connection._migrar_colunas_produto()  # não deve levantar exceção
