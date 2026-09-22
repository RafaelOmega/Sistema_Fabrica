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
