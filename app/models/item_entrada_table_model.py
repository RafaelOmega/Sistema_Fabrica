from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class ItemEntradaTableModel(QAbstractTableModel):
    HEADERS = ["Código", "Descrição", "Un", "Qtde", "Custo"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._itens = []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._itens)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if index.row() < 0 or index.row() >= len(self._itens):
            return None

        item = self._itens[index.row()]
        coluna = index.column()

        if role == Qt.DisplayRole:
            if coluna == 0:
                return item.get("codigo", "")
            if coluna == 1:
                return item.get("descricao", "")
            if coluna == 2:
                return item.get("unidade", "")
            if coluna == 3:
                qtde = item.get("quantidade", 0)
                return f"{qtde:.3f}"
            if coluna == 4:
                custo = item.get("custo", 0)
                return f"R$ {custo:.2f}"

        if role == Qt.TextAlignmentRole:
            if coluna in (2, 3, 4):
                return Qt.AlignCenter | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal and 0 <= section < len(self.HEADERS):
            return self.HEADERS[section]

        return str(section + 1)

    def atualizar_dados(self, itens):
        self.beginResetModel()
        self._itens = itens or []
        self.endResetModel()

    def obter_item(self, row):
        if 0 <= row < len(self._itens):
            return self._itens[row]
        return None

    def adicionar_item(self, item):
        self.beginInsertRows(
            QModelIndex(), len(self._itens), len(self._itens)
        )
        self._itens.append(item)
        self.endInsertRows()

    def atualizar_item(self, row, item):
        if 0 <= row < len(self._itens):
            self._itens[row] = item
            index = self.index(row, 0)
            index_fim = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(index, index_fim)

    def remover_item(self, row):
        if 0 <= row < len(self._itens):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._itens.pop(row)
            self.endRemoveRows()

    def limpar(self):
        self.beginResetModel()
        self._itens = []
        self.endResetModel()

    def obter_todos(self):
        return list(self._itens)

    @staticmethod
    def _formatar_custo(valor):
        if valor is None:
            return ""
        texto = f"{float(valor):.4f}".rstrip("0").rstrip(".")
        return texto.replace(".", ",") if texto else "0"
