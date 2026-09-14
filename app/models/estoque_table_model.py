from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class EstoqueTableModel(QAbstractTableModel):
    HEADERS = [
        "Código", "Descrição", "Entradas", "Saídas", "Saldo",
        "Custo", "Valor Total",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._linhas = []

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

        if index.row() < 0 or index.row() >= len(self._linhas):
            return None

        linha = self._linhas[index.row()]
        coluna = index.column()

        if role == Qt.DisplayRole:
            if coluna == 0:
                return linha.get("codigo", "")
            if coluna == 1:
                return linha.get("descricao", "")
            if coluna == 2:
                return f"{linha.get('qtd_entradas', 0):.3f}"
            if coluna == 3:
                return f"{linha.get('qtd_saidas', 0):.3f}"
            if coluna == 4:
                return f"{linha.get('saldo', 0):.3f}"
            if coluna == 5:
                return f"R$ {linha.get('custo', 0):.2f}"
            if coluna == 6:
                return f"R$ {linha.get('valor_total', 0):.2f}"

        if role == Qt.TextAlignmentRole:
            if coluna in (2, 3, 4, 5, 6):
                return Qt.AlignCenter | Qt.AlignVCenter
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
