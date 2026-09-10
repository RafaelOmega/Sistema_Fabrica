from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QSortFilterProxyModel, Qt


class EntradaFilterProxyModel(QSortFilterProxyModel):
    """Proxy customizado para pesquisa de entradas.
    Filtra por sequência, data e motivo, case-insensitive."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._texto_filtro = ""
        self.setDynamicSortFilter(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)

    def definir_filtro(self, texto):
        self._texto_filtro = (texto or "").strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self._texto_filtro:
            return True

        model = self.sourceModel()
        if model is None:
            return True

        entrada = model.obter_entrada(source_row)
        if entrada is None:
            return False

        conteudo = " ".join(
            [
                "" if entrada.get("sequencia") is None
                else str(entrada["sequencia"]),
                "" if entrada.get("data_entrada") is None
                else entrada["data_entrada"].strftime("%d/%m/%Y"),
                "" if entrada.get("motivo_descricao") is None
                else str(entrada["motivo_descricao"]),
            ]
        ).lower()

        return self._texto_filtro in conteudo

    def lessThan(self, left, right):
        model = self.sourceModel()
        if model is None:
            return super().lessThan(left, right)

        coluna = left.column()
        valor_esquerda = model.data(left, Qt.DisplayRole)
        valor_direita = model.data(right, Qt.DisplayRole)

        if coluna == 0:
            return self._comparar_sequencia(
                valor_esquerda, valor_direita
            )

        return str(valor_esquerda).lower() < str(valor_direita).lower()

    @staticmethod
    def _comparar_sequencia(valor_esquerda, valor_direita):
        try:
            num_esquerda = Decimal(str(valor_esquerda))
            num_direita = Decimal(str(valor_direita))
            return num_esquerda < num_direita
        except (InvalidOperation, ValueError, TypeError):
            return str(valor_esquerda).lower() < str(
                valor_direita
            ).lower()
