from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex


class FichaTecnicaTableModel(QAbstractTableModel):
    """Model para tb_Itens_Batida — itens com KG total da batida."""
    _HEADERS = ["Código", "Descrição", "Qtde Kg"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._itens = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._itens)

    def columnCount(self, parent=QModelIndex()):
        return len(self._HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = self._itens[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return item.get("codigo", "")
            elif col == 1:
                return item.get("descricao", "")
            elif col == 2:
                qtde = item.get("quantidade_kg", 0)
                return f"{float(qtde):.3f}".replace(".", ",")
        elif role == Qt.UserRole:
            if col == 2:
                return float(item.get("quantidade_kg", 0))
            if col == 0:
                return item.get("codigo", "")
            if col == 1:
                return item.get("descricao", "")
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._HEADERS[section]
        return None

    def adicionar_item(self, item):
        self.beginInsertRows(
            QModelIndex(), len(self._itens), len(self._itens)
        )
        self._itens.append(item)
        self.endInsertRows()
        self.layoutChanged.emit()

    def atualizar_item(self, row, item):
        if 0 <= row < len(self._itens):
            self._itens[row] = item
            self.dataChanged.emit(
                self.index(row, 0),
                self.index(row, self.columnCount() - 1),
            )
            self.layoutChanged.emit()

    def remover_item(self, row):
        if 0 <= row < len(self._itens):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._itens.pop(row)
            self.endRemoveRows()
            self.layoutChanged.emit()

    def obter_item(self, row):
        if 0 <= row < len(self._itens):
            return self._itens[row]
        return None

    def obter_todos(self):
        return self._itens.copy()

    def limpar(self):
        self.beginResetModel()
        self._itens.clear()
        self.endResetModel()

    def atualizar_dados(self, itens):
        self.beginResetModel()
        self._itens = list(itens)
        self.endResetModel()


class FichaTecnicaUnitarioTableModel(QAbstractTableModel):
    """Model para tb_Itens_Unitario — read-only, derivado de
    (kg_total / sacos_batida). Não é persistido."""
    _HEADERS = ["Código", "Descrição", "Kg/Saco"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._itens = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._itens)

    def columnCount(self, parent=QModelIndex()):
        return len(self._HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = self._itens[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return item.get("codigo", "")
            elif col == 1:
                return item.get("descricao", "")
            elif col == 2:
                qtde = float(item.get("quantidade_kg", 0) or 0)
                return f"{qtde:.6f}".replace(".", ",")
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._HEADERS[section]
        return None

    def atualizar_dados(self, itens):
        self.beginResetModel()
        self._itens = list(itens)
        self.endResetModel()

    def limpar(self):
        self.beginResetModel()
        self._itens.clear()
        self.endResetModel()
