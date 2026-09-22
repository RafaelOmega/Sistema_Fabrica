# app/models/kardex_table_model.py
from datetime import date

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

CASAS_QTD = 3
CASAS_VALOR = 4


class KardexTableModel(QAbstractTableModel):
    HEADERS = [
        "Código", "Descrição", "Data", "Tipo", "Qtde",
        "Custo Unit.", "Saldo Qtde", "Saldo Valor", "Custo Médio",
    ]

    # Índices de colunas numéricas: (coluna, casas decimais)
    COLUNAS_NUM = {
        4: CASAS_QTD,       # Qtde (assinada)
        5: CASAS_VALOR,     # Custo Unit.
        6: CASAS_QTD,       # Saldo Qtde
        7: 2,               # Saldo Valor
        8: CASAS_VALOR,     # Custo Médio
    }

    def __init__(self, linhas=None, parent=None):
        super().__init__(parent)
        self._linhas = linhas or []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._linhas)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        linha = self.obter_linha(index.row())
        if linha is None:
            return None

        coluna = index.column()

        if role == Qt.DisplayRole:
            if coluna == 0:
                return str(linha.get("codigo", ""))
            if coluna == 1:
                return str(linha.get("descricao", ""))
            if coluna == 2:
                return self._formatar_data(linha.get("data"))
            if coluna == 3:
                return self._rotulo_tipo(linha.get("tipo", ""))
            if coluna in self.COLUNAS_NUM:
                return self._formatar_numero(
                    linha.get(self._chave(coluna), 0),
                    self.COLUNAS_NUM[coluna],
                )
            return None

        if role == Qt.UserRole:
            # Valores brutos para ordenação numérica correta
            if coluna in self.COLUNAS_NUM:
                return float(linha.get(self._chave(coluna), 0) or 0)
            if coluna == 2:
                return linha.get("data") or date.min
            return None

        if role == Qt.TextAlignmentRole:
            if coluna in self.COLUNAS_NUM:
                return Qt.AlignRight | Qt.AlignVCenter
            if coluna in (2, 3):
                return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal and 0 <= section < len(self.HEADERS):
            return self.HEADERS[section]
        return str(section + 1)

    def atualizar_dados(self, linhas):
        self.beginResetModel()
        self._linhas = linhas or []
        self.endResetModel()

    def obter_linha(self, row):
        if 0 <= row < len(self._linhas):
            return self._linhas[row]
        return None

    def obter_todos(self):
        return list(self._linhas)

    # --- Helpers ---

    @staticmethod
    def _chave(coluna):
        return {
            4: "quantidade",
            5: "custo_unitario",
            6: "saldo_quantidade",
            7: "saldo_valor",
            8: "custo_medio",
        }[coluna]

    @staticmethod
    def _rotulo_tipo(tipo):
        return {
            "ENTRADA": "Entrada",
            "SAIDA": "Saída",
            "CONSUMO_PRODUCAO": "Consumo Produção",
            "AJUSTE": "Ajuste",
        }.get(tipo, tipo)

    @staticmethod
    def _formatar_data(valor):
        if valor is None:
            return ""
        if isinstance(valor, date):
            return valor.strftime("%d/%m/%Y")
        return str(valor)

    @staticmethod
    def _formatar_numero(valor, casas):
        if valor is None:
            return ""
        texto = f"{float(valor):.{casas}f}".rstrip("0").rstrip(".")
        return texto.replace(".", ",") if texto else "0"
