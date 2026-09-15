from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
)

from app.models.produto_filter_proxy_model import ProdutoFilterProxyModel
from app.models.produto_table_model import ProdutoTableModel
from app.services.produto_service import ProdutoService
from app.utils.logger import get_logger
from app.utils.table_utils import configurar_tabela
from app.views.ui_pesquisa_Produto import Ui_Pesquisa_Prod

logger = get_logger("pesquisa_produto_controller")


class PesquisaProdutoController(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Pesquisa_Prod()
        self.ui.setupUi(self)

        self.service = ProdutoService()
        self.model = ProdutoTableModel()
        self.proxy_model = ProdutoFilterProxyModel(self)

        self.produto_selecionado = None

        self._configurar_tabela()
        self._conectar_sinais()
        self._carregar_dados()

    def _configurar_tabela(self):
        self.proxy_model.setSourceModel(self.model)
        self.ui.tb_Produtos.setModel(self.proxy_model)
        configurar_tabela(self.ui.tb_Produtos,
                          coluna_stretch=1, ordenavel=True)

    def _conectar_sinais(self):
        self.ui.txt_Pesquisa.textChanged.connect(self._aplicar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self.confirmar)
        self.ui.tb_Produtos.doubleClicked.connect(self.confirmar)

    def _carregar_dados(self):
        try:
            produtos = self.service.listar_todos()
            self.model.atualizar_dados(produtos)
        except Exception as e:
            logger.error(f"Erro ao carregar produtos: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao carregar: {e}")

    def _aplicar_filtro(self):
        texto = self.ui.txt_Pesquisa.text().strip()
        self.proxy_model.definir_filtro(texto)

    def confirmar(self):
        indexes = self.ui.tb_Produtos.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Aviso", "Selecione um produto.")
            return

        index_proxy = indexes[0]
        index_source = self.proxy_model.mapToSource(index_proxy)
        self.produto_selecionado = self.model.obter_produto(index_source.row())

        if self.produto_selecionado:
            logger.debug(
                f"Produto selecionado: {self.produto_selecionado.codigo}"
            )
            self.accept()
