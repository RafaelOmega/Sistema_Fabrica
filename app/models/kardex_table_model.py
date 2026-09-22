# app/models/kardex_table_model.py
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

CASAS_QTD = 3
CASAS_VALOR = 4


def _fmt(valor, casas):
    """Formata número no padrão brasileiro (1.234,5678)."""
    txt = f"{valor:,.{casas}f}"
    return txt.replace(",", "X").replace(".", ",").replace("X", ".")


class KardexTableModel(QAbstractTableModel):
    HEADER = [
        "Código", "Descrição", "Data", "Tipo", "Qtde",
        "Custo Unit.", "Saldo Qtde", "Saldo Valor", "Custo Médio",
    ]

    # coluna -> casas decimais
    COLUNAS_NUM = {
        4: CASAS_QTD,       # Qtde (assinada)
        5: CASAS_VALOR,     # Custo Unit.
        6: CASAS_QTD,       # Saldo Qtde
        7: CASAS_VALOR,     # Saldo Valor
        8: CASAS_VALOR,     # Custo Médio
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._linhas = []  # lista de dicts (dados já materializados)

    # --- Estrutura básica ---

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._linhas)

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADER)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADER[section]
        return None

    # --- Dados ---

    def dados_celula(self, linha, coluna):
        """Valor cru/formatado da célula. Usado pela view e pela exportação."""
        r = self._linhas[linha]

        if coluna == 0:
            return str(r["codigo"])
        if coluna == 1:
            return str(r["descricao"])
        if coluna == 2:
            data = r["data"]
            return data.strftime("%d/%m/%Y") if data else ""
        if coluna == 3:
            return str(r["tipo"])

        casas = self.COLUNAS_NUM.get(coluna)
        if casas is None:
            return ""
        return _fmt(r[self._CAMPO[coluna]], casas)

    # campo do dict para cada coluna numérica
    _CAMPO = {
        4: "quantidade",
        5: "custo_unitario",
        6: "saldo_quantidade",
        7: "saldo_valor",
        8: "custo_medio",
    }

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        linha, coluna = index.row(), index.column()

        if role == Qt.DisplayRole:
            return self.dados_celula(linha, coluna)

        if role == Qt.TextAlignmentRole and coluna in self.COLUNAS_NUM:
            return int(Qt.AlignRight | Qt.AlignVCenter)

        if role == Qt.BackgroundRole:
            if coluna in (4, 7) and self._linhas[linha]["tipo"] != "ENTRADA":
                return QColor(255, 235, 235)
        return None

    def atualizar_dados(self, linhas):
        self.beginResetModel()
        self._linhas = list(linhas)
        self.endResetModel()

    @property
    def linhas(self):
        return self._linhas
