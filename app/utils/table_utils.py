from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QAbstractItemView, QHeaderView

# Largura máxima (px) que uma coluna pode assumir automaticamente.
# Evita que uma descrição muito longa empurre todas as outras colunas
# para fora da área visível.
LARGURA_MAXIMA_PADRAO = 400

# Largura mínima (px) de qualquer coluna, para que nunca fique
# ilegível (era exatamente o que acontecia com a Descrição: o modo
# Stretch a reduzia ao mínimo do Qt quando não sobrava espaço).
LARGURA_MINIMA_PADRAO = 60


def configurar_tabela(table_view, coluna_stretch=None, ordenavel=False,
                      selecionavel=True,
                      largura_maxima=LARGURA_MAXIMA_PADRAO):
    """
    Configuração padrão de uma QTableView, com dimensionamento
    AUTOMÁTICO das colunas.

    Por que não usar simplesmente QHeaderView.Stretch na coluna
    principal: o modo Stretch só distribui o espaço que SOBRA depois
    das demais colunas. Quando as outras colunas são largas (por
    exemplo os cabeçalhos "Prod. Acabado", "Mat. Prima", "Mão de
    Obra", "Controla Estoque" na tela de Produtos), não sobra espaço
    e a coluna "esticável" acaba encolhendo até o mínimo — a
    descrição aparecia cortada como "Balance...".

    A abordagem aqui é outra:
      1. mede a largura de cada coluna pelo CONTEÚDO real
         (resizeColumnsToContents);
      2. limita cada coluna a `largura_maxima`, para uma descrição
         muito longa não expulsar as demais colunas da tela;
      3. se ainda sobrar espaço horizontal, a folga vai toda para
         `coluna_stretch`;
      4. se não couber, aparece rolagem horizontal — melhor do que
         truncar o texto.

    O ajuste é reaplicado sozinho quando os dados mudam e quando a
    tabela é redimensionada.

    Args:
        table_view: a QTableView já com o model definido (chame isto
            DEPOIS de setModel).
        coluna_stretch: índice da coluna que recebe a folga
            horizontal (tipicamente descrição/nome). None = nenhuma.
        ordenavel: cabeçalho clicável para ordenar. Use em telas de
            listagem/pesquisa; mantenha False em tabelas de itens em
            edição (ordenar bagunçaria a correlação entre a linha
            selecionada e o índice do item em memória).
        selecionavel: False para tabelas somente leitura sem seleção.
        largura_maxima: teto em px para a largura automática.
    """
    if selecionavel:
        table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_view.setSelectionMode(QAbstractItemView.SingleSelection)
    else:
        table_view.setSelectionMode(QAbstractItemView.NoSelection)

    table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table_view.setAlternatingRowColors(True)
    table_view.setSortingEnabled(ordenavel)
    table_view.verticalHeader().setVisible(False)
    table_view.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    header = table_view.horizontalHeader()
    header.setStretchLastSection(False)
    # Interactive (em vez de Stretch/ResizeToContents) porque nós
    # mesmos calculamos as larguras em ajustar_larguras(); isso
    # também deixa o usuário arrastar a divisória se quiser.
    header.setSectionResizeMode(QHeaderView.Interactive)
    header.setMinimumSectionSize(LARGURA_MINIMA_PADRAO)

    _AjustadorDeColunas(table_view, coluna_stretch, largura_maxima)
    ajustar_larguras(table_view, coluna_stretch, largura_maxima)


def ajustar_larguras(table_view, coluna_stretch=None,
                     largura_maxima=LARGURA_MAXIMA_PADRAO):
    """Recalcula as larguras com base no conteúdo atual da tabela."""
    modelo = table_view.model()
    if modelo is None:
        return

    num_colunas = modelo.columnCount()
    if num_colunas == 0:
        return

    header = table_view.horizontalHeader()

    # 1. Largura pelo conteúdo real (considera cabeçalho e células).
    table_view.resizeColumnsToContents()

    # 2. Aplica teto/piso por coluna.
    for coluna in range(num_colunas):
        largura = header.sectionSize(coluna)
        if largura > largura_maxima:
            table_view.setColumnWidth(coluna, largura_maxima)
        elif largura < LARGURA_MINIMA_PADRAO:
            table_view.setColumnWidth(coluna, LARGURA_MINIMA_PADRAO)

    # 3. Sobra de espaço vai toda para a coluna principal.
    if coluna_stretch is None or not (0 <= coluna_stretch < num_colunas):
        return

    total = sum(header.sectionSize(c) for c in range(num_colunas))
    disponivel = table_view.viewport().width()

    if disponivel > total:
        folga = disponivel - total
        table_view.setColumnWidth(
            coluna_stretch, header.sectionSize(coluna_stretch) + folga
        )


class _AjustadorDeColunas(QObject):
    """Reaplica ajustar_larguras() quando os dados mudam ou a tabela
    é redimensionada.

    É instanciado com o table_view como parent para que o Qt mantenha
    a referência viva — sem isso o objeto seria coletado pelo garbage
    collector do Python e o filtro de eventos pararia de funcionar
    silenciosamente.
    """

    def __init__(self, table_view, coluna_stretch, largura_maxima):
        super().__init__(table_view)
        self._table_view = table_view
        self._coluna_stretch = coluna_stretch
        self._largura_maxima = largura_maxima

        table_view.viewport().installEventFilter(self)

        modelo = table_view.model()
        if modelo is not None:
            modelo.modelReset.connect(self._ajustar)
            modelo.rowsInserted.connect(self._ajustar)
            modelo.rowsRemoved.connect(self._ajustar)
            modelo.dataChanged.connect(self._ajustar)
            modelo.layoutChanged.connect(self._ajustar)

    def _ajustar(self, *args):
        ajustar_larguras(
            self._table_view, self._coluna_stretch, self._largura_maxima
        )

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self._ajustar()
        return super().eventFilter(obj, event)
