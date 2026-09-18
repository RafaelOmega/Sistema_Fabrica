from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QSortFilterProxyModel, Qt


class FichaTecnicaFilterProxyModel(QSortFilterProxyModel):
    """Proxy customizado para pesquisa de fichas técnicas.
    Filtra por id da ficha, código e descrição do produto acabado,
    case-insensitive.

    Segue o mesmo padrão de ProdutoFilterProxyModel/SaidaFilterProxyModel/
    MotivoEntradaFilterProxyModel: filtro em texto único aplicado sobre
    o dict retornado por `obter_ficha`, e comparação numérica no código
    para ordenação correta (sem isso "10" viria antes de "2")."""

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

        ficha = model.obter_ficha(source_row)
        if ficha is None:
            return False

        conteudo = " ".join(
            [
                "" if ficha.get("id") is None
                else str(ficha["id"]),
                "" if ficha.get("codigo") is None
                else str(ficha["codigo"]),
                "" if ficha.get("descricao") is None
                else str(ficha["descricao"]),
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

        # Coluna 0 = id da ficha, coluna 1 = código do produto acabado —
        # ambos numéricos, então usam a mesma comparação segura (sem
        # isso "10" ficaria antes de "2" na ordenação por texto).
        if coluna in (0, 1):
            return self._comparar_codigo(valor_esquerda, valor_direita)

        return str(valor_esquerda).lower() < str(valor_direita).lower()

    @staticmethod
    def _comparar_codigo(valor_esquerda, valor_direita):
        try:
            num_esquerda = Decimal(str(valor_esquerda))
            num_direita = Decimal(str(valor_direita))
            return num_esquerda < num_direita
        except (InvalidOperation, ValueError, TypeError):
            return str(valor_esquerda).lower() < str(valor_direita).lower()
