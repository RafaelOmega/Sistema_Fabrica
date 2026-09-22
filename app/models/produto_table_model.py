from decimal import Decimal

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class ProdutoTableModel(QAbstractTableModel):
    HEADERS = ["Código", "Descrição", "Peso",
               "Custo", "Prod. Acabado", "Mat. Prima",
               "Mão de Obra", "Controla Estoque"]

    def __init__(self, produtos=None, parent=None):
        super().__init__(parent)
        self._produtos = produtos or []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._produtos)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        produto = self.obter_produto(index.row())
        if produto is None:
            return None

        coluna = index.column()

        if role == Qt.DisplayRole:
            if coluna == 0:
                return "" if produto.codigo is None else str(produto.codigo)
            if coluna == 1:
                return "" if produto.descricao is None else str(produto.descricao)
            if coluna == 2:
                return self._formatar_peso(produto.peso)
            if coluna == 3:
                return self._formatar_custo(produto.custo)
            if coluna == 4:
                return "Sim" if getattr(produto, "prod_acabado", False) else "Não"
            if coluna == 5:
                return "Sim" if getattr(produto, "mat_prima", False) else "Não"
            if coluna == 6:
                return "Sim" if getattr(produto, "mao_obra", False) else "Não"
            if coluna == 7:
                return "Sim" if getattr(produto, "controla_estoque", False) else "Não"

        if role == Qt.UserRole:
            if coluna == 0:
                return "" if produto.codigo is None else str(produto.codigo)
            if coluna == 1:
                return "" if produto.descricao is None else str(produto.descricao)
            if coluna == 2:
                return self._to_float(produto.peso)
            if coluna == 3:
                return self._to_decimal(produto.custo)
            if coluna == 4:
                return bool(getattr(produto, "prod_acabado", False))
            if coluna == 5:
                return bool(getattr(produto, "mat_prima", False))
            if coluna == 6:
                return bool(getattr(produto, "mao_obra", False))
            if coluna == 7:
                return bool(getattr(produto, "controla_estoque", False))

        if role == Qt.TextAlignmentRole:
            if coluna in (2, 3):
                return Qt.AlignRight | Qt.AlignVCenter
            if coluna in (4, 5, 6, 7):
                return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal and 0 <= section < len(self.HEADERS):
            return self.HEADERS[section]
        return str(section + 1)

    def atualizar_dados(self, produtos):
        self.beginResetModel()
        self._produtos = produtos or []
        self.endResetModel()

    def obter_produto(self, row):
        if 0 <= row < len(self._produtos):
            return self._produtos[row]
        return None

    @staticmethod
    def _formatar_peso(valor):
        if valor is None:
            return ""
        texto = f"{float(valor):.4f}".rstrip("0").rstrip(".")
        return texto.replace(".", ",") if texto else "0"

    @staticmethod
    def _formatar_custo(valor):
        if valor is None:
            return "0"
        if isinstance(valor, Decimal):
            texto = format(valor, ".4f").rstrip("0").rstrip(".")
        else:
            texto = f"{float(valor):.4f}".rstrip("0").rstrip(".")
        return texto.replace(".", ",") if texto else "0"

    @staticmethod
    def _to_float(valor):
        if valor is None:
            return 0.0
        return float(valor)

    @staticmethod
    def _to_decimal(valor):
        if valor is None:
            return Decimal("0.00")
        if isinstance(valor, Decimal):
            return valor
        return Decimal(str(valor))
