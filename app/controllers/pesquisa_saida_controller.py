from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHeaderView,
    QMessageBox,
)
from app.models.saida_filter_proxy_model import SaidaFilterProxyModel
from app.models.saida_table_model import SaidaTableModel
from app.services.saida_service import SaidaService
from app.utils.logger import get_logger
from app.views.ui_pesquisa_Saida import Ui_Pesquisa_Prod as Ui_Pesquisa_Saida

logger = get_logger("pesquisa_saida_controller")


class PesquisaSaidaController(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Pesquisa_Saida()
        self.ui.setupUi(self)

        self.service = SaidaService()
        self.model = SaidaTableModel()
        self.proxy_model = SaidaFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.saida_selecionada = None

        self._configurar_tabela()
        self._conectar_sinais()
        self._carregar_dados()

    def _configurar_tabela(self):
        self.ui.tb_Saidas.setModel(self.proxy_model)
        self.ui.tb_Saidas.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.ui.tb_Saidas.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.ui.tb_Saidas.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.ui.tb_Saidas.setAlternatingRowColors(True)
        self.ui.tb_Saidas.setSortingEnabled(True)
        self.ui.tb_Saidas.verticalHeader().setVisible(False)

        header = self.ui.tb_Saidas.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def _conectar_sinais(self):
        self.ui.txt_Pesquisa.textChanged.connect(self._aplicar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self.confirmar)
        self.ui.tb_Saidas.doubleClicked.connect(self.confirmar)

    def _carregar_dados(self):
        try:
            saidas = self.service.listar_todos()
            self.model.atualizar_dados(saidas)
        except Exception as e:
            logger.error(f"Erro ao carregar saídas: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao carregar: {e}")

    def _aplicar_filtro(self):
        texto = self.ui.txt_Pesquisa.text().strip()
        self.proxy_model.definir_filtro(texto)

    def confirmar(self):
        indexes = self.ui.tb_Saidas.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Aviso", "Selecione uma saída.")
            return

        index_proxy = indexes[0]
        index_source = self.proxy_model.mapToSource(index_proxy)
        self.saida_selecionada = self.model.obter_saida(
            index_source.row()
        )

        if self.saida_selecionada:
            logger.debug(
                f"Saída selecionada: "
                f"{self.saida_selecionada.get('sequencia')}"
            )
            self.accept()
