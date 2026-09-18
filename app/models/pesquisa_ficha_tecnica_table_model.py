from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex


class PesquisaFichaTecnicaTableModel(QAbstractTableModel):
    """Model para tb_Fichas_Tecnicas — listagem de fichas técnicas.

    A ficha técnica não tem mais um código próprio digitado pelo
    usuário: ela é identificada pelo seu id no banco (autoincrement),
    exibido na coluna "Ficha". Código/descrição seguem mostrados como
    referência do produto acabado ao qual a ficha pertence."""
    _HEADERS = ["Ficha", "Cód. Prod. Acabado", "Descrição", "Sacos/Batida"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fichas = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._fichas)

    def columnCount(self, parent=QModelIndex()):
        return len(self._HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        ficha = self._fichas[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return str(ficha.get("id", ""))
            elif col == 1:
                return ficha.get("codigo", "")
            elif col == 2:
                return ficha.get("descricao", "")
            elif col == 3:
                return str(ficha.get("sacos_batida", 0))
        elif role == Qt.UserRole:
            return ficha
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._HEADERS[section]
        return None

    def atualizar_dados(self, fichas):
        self.beginResetModel()
        self._fichas = list(fichas)
        self.endResetModel()

    def obter_ficha(self, row):
        if 0 <= row < len(self._fichas):
            return self._fichas[row]
        return None
