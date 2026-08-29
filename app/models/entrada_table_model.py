from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class EntradaTableModel(QAbstractTableModel):
    HEADERS = ["Sequência", "Data", "Motivo"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entradas = []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._entradas)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if index.row() < 0 or index.row() >= len(self._entradas):
            return None

        entrada = self._entradas[index.row()]
        coluna = index.column()

        if role == Qt.DisplayRole:
            if coluna == 0:
                return entrada.get("sequencia", "")
            if coluna == 1:
                data = entrada.get("data_entrada")
                if data:
                    return data.strftime("%d/%m/%Y")
                return ""
            if coluna == 2:
                return entrada.get("motivo_descricao", "")

        if role == Qt.TextAlignmentRole:
            if coluna == 0:
                return Qt.AlignCenter | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal and 0 <= section < len(self.HEADERS):
            return self.HEADERS[section]

        return str(section + 1)

    def atualizar_dados(self, entradas):
        self.beginResetModel()
        self._entradas = entradas or []
        self.endResetModel()

    def obter_entrada(self, row):
        if 0 <= row < len(self._entradas):
            return self._entradas[row]
        return None
