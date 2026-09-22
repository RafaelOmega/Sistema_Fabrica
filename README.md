# Sistema_Fabrica

Sistema desktop para controle de estoque e produção de uma fábrica pequena.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Qt](https://img.shields.io/badge/GUI-PySide6-green)
![DB](https://img.shields.io/badge/Banco-PostgreSQL-blue)

## Funcionalidades

- **Cadastro de Produtos** — código, descrição, peso e custo (4 casas decimais), tipo
  (produto acabado, matéria-prima, mão de obra) e flag de controle de estoque.
  Pesquisa em tela dedicada; exclusão protegida contra produtos vinculados.
- **Entrada de Mercadorias** — notas com múltiplos itens, motivo de entrada e
  detecção de alteração de custo (registrada e aplicada transacionalmente).
- **Saída de Mercadorias** — notas com itens, sequência numérica gerada
  automaticamente com prevenção de colisão.
- **Ficha Técnica** — composição de produtos (receita em kg por item).
- **Estoque** — saldo por produto em data-base, com ocultação de zerados e
  exportação para Excel.
- **Kardex** — movimentação com custo médio ponderado móvel, sempre
  sincronizada com entradas/saídas (inclusive em edições e exclusões).
- **Motivos de Entrada** e **Regras de Produtos Especiais** — configuráveis no
  banco, sem necessidade de novo build.

## Arquitetura

Camadas bem separadas — nenhuma regra de negócio consulta o banco direto da tela:
app/

app/
├── controllers/   # Telas Qt (MDI), orquestração de UI
├── services/      # Regras de negócio e validações
├── repositories/  # Acesso a dados (SQLAlchemy ORM)
├── models/        # Entidades ORM + Table Models/Proxy Models Qt
├── database/      # Engine, sessões e inicialização
├── views/         # UIs geradas do Qt Designer (.ui + .py)
├── utils/         # Logger, tema, helpers de tabela
└── styles/        # Tema escuro (QSS)
tests/ # Testes unitários e de integração (pytest) build.bat # Build do executável Windows (PyInstaller)


**Stack:** Python · PySide6 (Qt 6) · SQLAlchemy 2.0 · PostgreSQL · openpyxl · PyInstaller · pytest

## Configuração

As credenciais do banco são lidas de **variáveis de ambiente** (o app falha
imediatamente se não estiverem definidas):

| Variável      | Descrição                          | Exemplo          |
|---------------|------------------------------------|------------------|
| `DB_USER`     | usuário do PostgreSQL              | `fabrica`        |
| `DB_PASSWORD` | senha do PostgreSQL (**obrigatória**) | `••••••`      |
| `DB_HOST`     | host do servidor                   | `192.168.0.10`   |
| `DB_PORT`     | porta                              | `5432`           |
| `DB_NAME`     | nome do banco                      | `fabrica`        |
| `DB_SSLMODE`  | modo SSL (opcional)                | `require`        |

## Como rodar

```bash
git clone https://github.com/RafaelOmega/Sistema_Fabrica.git
cd Sistema_Fabrica
pip install -r requirements.txt

# defina as variáveis de ambiente (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
python main.py
As tabelas são criadas automaticamente na inicialização (init_db()).
