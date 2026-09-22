# app/controllers/kardex_controller.py
from datetime import date

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QDialog, QMessageBox, QWidget

from app.repositories.movimento_estoque_repository import (
    MovimentoEstoqueRepository,
)
from app.repositories.produto_repository import ProdutoRepository
from app.utils.logger import get_logger
from app.utils.table_utils import configurar_tabela
from app.views.ui_movimento_estoque import Ui_Movimento_Estoque

logger = get_logger("kardex_controller")

CASAS_QTD = 3
CASAS_VALOR = 4


class KardexController(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Movimento_Estoque()
        self.ui.setupUi(self)

        self.repo = MovimentoEstoqueRepository()
        self.produto_repo = ProdutoRepository()
        self.produto_id = None

        from app.models.kardex_table_model import KardexTableModel
        self.model = KardexTableModel()

        self._configurar_tabela()
        self._configurar_campos()
        self._conectar_sinais()
        self._estado_inicial()
        logger.info("Tela de kardex inicializada")

    # --- Configuração ---

    def _configurar_tabela(self):
        self.ui.tb_Kardex.setModel(self.model)
        configurar_tabela(self.ui.tb_Kardex, coluna_stretch=1,
                          ordenavel=True)

    def _configurar_campos(self):
        self.ui.dt_Produto.setCalendarPopup(True)
        self.ui.dt_Produto.setDisplayFormat("dd/MM/yyyy")
        self.ui.dt_Produto.setDate(QDate.currentDate())

    def _conectar_sinais(self):
        self.ui.bt_Pesquisar_Produto.clicked.connect(
            self.abrir_pesquisa_produto)
        self.ui.bt_Atualizar.clicked.connect(self.atualizar)

    # --- Pesquisa do produto ---

    def abrir_pesquisa_produto(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )
        dialog = PesquisaProdutoController(self)
        if dialog.exec() != QDialog.Accepted:
            return
        produto = dialog.produto_selecionado
        if produto is None:
            return
        self.produto_id = produto.id
        self.ui.lb_Produto.setText(
            f"{produto.codigo} - {produto.descricao}")
        self.atualizar()

    # --- Dados ---

    def atualizar(self):
        if self.produto_id is None:
            QMessageBox.warning(
                self, "Aviso", "Selecione um produto primeiro.")
            return
        try:
            linhas = self.repo.listar_por_produto(self.produto_id)
            self.model.atualizar_dados(linhas)
            logger.info(
                f"Kardex atualizado | produto_id={self.produto_id} "
                f"| movimentos={len(linhas)}")
        except Exception as e:
            logger.error(f"Erro ao atualizar kardex: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar: {e}")

    def _estado_inicial(self):
        self.ui.bt_Atualizar.setEnabled(False)
