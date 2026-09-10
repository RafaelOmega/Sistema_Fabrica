from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHeaderView,
    QMessageBox,
)
from app.models.entrada_filter_proxy_model import EntradaFilterProxyModel
from app.models.entrada_table_model import EntradaTableModel
from app.services.entrada_service import EntradaService
from app.utils.logger import get_logger
from app.views.ui_pesquisa_Entrada import Ui_Pesquisa_Prod as Ui_Pesquisa_Entrada

logger = get_logger("pesquisa_entrada_controller")


class PesquisaEntradaController(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Pesquisa_Entrada()
        self.ui.setupUi(self)

        self.service = EntradaService()
        self.model = EntradaTableModel()
        self.proxy_model = EntradaFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.entrada_selecionada = None

        self._configurar_tabela()
        self._conectar_sinais()
        self._carregar_dados()

    def _configurar_tabela(self):
        self.ui.tb_Entradas.setModel(self.proxy_model)
        self.ui.tb_Entradas.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.ui.tb_Entradas.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.ui.tb_Entradas.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.ui.tb_Entradas.setAlternatingRowColors(True)
        self.ui.tb_Entradas.setSortingEnabled(True)
        self.ui.tb_Entradas.verticalHeader().setVisible(False)

        header = self.ui.tb_Entradas.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

    def _conectar_sinais(self):
        self.ui.txt_Pesquisa.textChanged.connect(self._aplicar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self.confirmar)
        self.ui.tb_Entradas.doubleClicked.connect(self.confirmar)

    def _carregar_dados(self):
        try:
            entradas = self.service.listar_todos()
            self.model.atualizar_dados(entradas)
        except Exception as e:
            logger.error(f"Erro ao carregar entradas: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao carregar: {e}")

    def _aplicar_filtro(self):
        texto = self.ui.txt_Pesquisa.text().strip()
        self.proxy_model.definir_filtro(texto)

    def confirmar(self):
        indexes = self.ui.tb_Entradas.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Aviso", "Selecione uma entrada.")
            return

        index_proxy = indexes[0]
        index_source = self.proxy_model.mapToSource(index_proxy)
        self.entrada_selecionada = self.model.obter_entrada(
            index_source.row()
        )

        if self.entrada_selecionada:
            logger.debug(
                f"Entrada selecionada: "
                f"{self.entrada_selecionada.get('sequencia')}"
            )
            self.accept()
