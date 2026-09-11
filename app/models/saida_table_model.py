from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class SaidaTableModel(QAbstractTableModel):
    HEADERS = ["Sequência", "Data"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._saidas = []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._saidas)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if index.row() < 0 or index.row() >= len(self._saidas):
            return None

        saida = self._saidas[index.row()]
        coluna = index.column()

        if role == Qt.DisplayRole:
            if coluna == 0:
                return saida.get("sequencia", "")
            if coluna == 1:
                data = saida.get("data_saida")
                if data:
                    return data.strftime("%d/%m/%Y")
                return ""

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

    def atualizar_dados(self, saidas):
        self.beginResetModel()
        self._saidas = saidas or []
        self.endResetModel()

    def obter_saida(self, row):
        if 0 <= row < len(self._saidas):
            return self._saidas[row]
        return None
