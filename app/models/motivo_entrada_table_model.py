from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class MotivoEntradaTableModel(QAbstractTableModel):
    HEADERS = ["Código", "Descrição"]

    def __init__(self, motivos=None, parent=None):
        super().__init__(parent)
        self._motivos = motivos or []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._motivos)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        motivo = self.obter_motivo(index.row())
        if motivo is None:
            return None

        coluna = index.column()

        if role == Qt.DisplayRole:
            if coluna == 0:
                return "" if motivo.codigo is None else str(motivo.codigo)
            if coluna == 1:
                return "" if motivo.descricao is None else str(motivo.descricao)

        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal and 0 <= section < len(self.HEADERS):
            return self.HEADERS[section]

        return str(section + 1)

    def atualizar_dados(self, motivos):
        self.beginResetModel()
        self._motivos = motivos or []
        self.endResetModel()

    def obter_motivo(self, row):
        if 0 <= row < len(self._motivos):
            return self._motivos[row]
        return None
