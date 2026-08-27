# app/controllers/cad_produtos_controller.py

from PySide6.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PySide6.QtCore import Qt
from app.views.ui_produtos import Ui_Produtos
from app.services.produto_service import ProdutoService
from app.utils.logger import get_logger

logger = get_logger("produtos_controller")


class ProdutosController(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Produtos()
        self.ui.setupUi(self)

        self.service = ProdutoService()
        self.produto_selecionado_id = None

        self._configurar_tabela()
        self._conectar_sinais()
        self._carregar_dados()
        logger.info("Tela de produtos inicializada")

    def _configurar_tabela(self):
        self.ui.tb_Produtos.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.ui.tb_Produtos.setSelectionBehavior(
            self.ui.tb_Produtos.SelectionBehavior.SelectRows
        )
        self.ui.tb_Produtos.setEditTriggers(
            self.ui.tb_Produtos.EditTrigger.NoEditTriggers
        )

    def _conectar_sinais(self):
        self.ui.bt_Salvar.clicked.connect(self.salvar)
        self.ui.bt_Editar.clicked.connect(self.editar)
        self.ui.bt_Limpar.clicked.connect(self.limpar)
        self.ui.bt_Excluir.clicked.connect(self.excluir)
        self.ui.bt_Pesquisar.clicked.connect(self.pesquisar)
        self.ui.tb_Produtos.cellClicked.connect(self.selecionar_linha)

    def _bloquear_campos(self):
        """Bloqueia campos exceto bt_Editar e bt_Limpar (cancelar)."""
        for widget in [
            self.ui.txt_Codigo, self.ui.txt_Descricao, self.ui.txt_Peso,
            self.ui.txt_Custo, self.ui.txt_Pesquisar,
            self.ui.bt_Salvar, self.ui.bt_Excluir, self.ui.bt_Pesquisar
        ]:
            widget.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)

    def _desbloquear_tudo(self, bloquear_editar=False):
        """Desbloqueia tudo. Se bloquear_editar=True, desabilita só o bt_Editar."""
        for widget in [
            self.ui.txt_Codigo, self.ui.txt_Descricao, self.ui.txt_Peso,
            self.ui.txt_Custo, self.ui.txt_Pesquisar,
            self.ui.bt_Salvar, self.ui.bt_Limpar,
            self.ui.bt_Excluir, self.ui.bt_Pesquisar
        ]:
            widget.setEnabled(True)
        self.ui.bt_Editar.setEnabled(not bloquear_editar)

    def _carregar_dados(self, produtos=None):
        if produtos is None:
            produtos = self.service.listar_todos()

        self.ui.tb_Produtos.setRowCount(0)
        for row, prod in enumerate(produtos):
            self.ui.tb_Produtos.insertRow(row)
            self.ui.tb_Produtos.setItem(row, 0, QTableWidgetItem(prod.codigo))
            self.ui.tb_Produtos.setItem(
                row, 1, QTableWidgetItem(prod.descricao))
            self.ui.tb_Produtos.setItem(
                row, 2, QTableWidgetItem(f"{prod.peso:.2f}"))
            self.ui.tb_Produtos.setItem(
                row, 3, QTableWidgetItem(f"{prod.custo:.2f}"))
            self.ui.tb_Produtos.item(row, 0).setData(Qt.UserRole, prod.id)
        logger.debug(f"Tabela carregada: {len(produtos)} produtos")

    def salvar(self):
        codigo = self.ui.txt_Codigo.text().strip()
        descricao = self.ui.txt_Descricao.text().strip()
        peso = self.ui.txt_Peso.value()
        custo = self.ui.txt_Custo.value()

        if not codigo or not descricao:
            logger.warning("Tentativa de salvar sem código ou descrição")
            QMessageBox.warning(self, "Aviso", "Preencha código e descrição.")
            return

        try:
            self.service.salvar(codigo, descricao, peso,
                                custo, self.produto_selecionado_id)
            logger.info(f"Produto salvo com sucesso: codigo={codigo}")
            self.limpar()
            self._carregar_dados()
            QMessageBox.information(
                self, "Sucesso", "Produto salvo com sucesso.")
        except ValueError as e:
            logger.warning(f"Falha ao salvar produto: {e}")
            QMessageBox.warning(self, "Erro", str(e))
        except Exception as e:
            logger.error(f"Erro inesperado ao salvar: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    def editar(self):
        if self.produto_selecionado_id is None:
            QMessageBox.warning(
                self, "Aviso", "Selecione um produto na tabela.")
            return
        self._desbloquear_tudo(bloquear_editar=True)
        logger.debug(f"Modo edição ativado: ID={self.produto_selecionado_id}")

    def limpar(self):
        self.ui.txt_Codigo.clear()
        self.ui.txt_Descricao.clear()
        self.ui.txt_Peso.setValue(0.0)
        self.ui.txt_Custo.setValue(0.0)
        self.ui.txt_Pesquisar.clear()
        self.produto_selecionado_id = None
        self._desbloquear_tudo()
        self._carregar_dados()

    def excluir(self):
        if self.produto_selecionado_id is None:
            QMessageBox.warning(
                self, "Aviso", "Selecione um produto na tabela.")
            return

        resposta = QMessageBox.question(
            self, "Confirmar",
            "Deseja realmente excluir este produto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self.service.excluir(self.produto_selecionado_id)
                logger.info(
                    f"Produto excluído: ID={self.produto_selecionado_id}")
                self.limpar()
                self._carregar_dados()
                QMessageBox.information(self, "Sucesso", "Produto excluído.")
            except ValueError as e:
                logger.warning(f"Falha ao excluir: {e}")
                QMessageBox.warning(self, "Erro", str(e))
            except Exception as e:
                logger.error(f"Erro inesperado ao excluir: {e}", exc_info=True)
                QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    def pesquisar(self):
        termo = self.ui.txt_Pesquisar.text().strip()
        produtos = self.service.pesquisar(
            termo) if termo else self.service.listar_todos()
        self._carregar_dados(produtos)
        logger.debug(
            f"Pesquisa realizada: termo='{termo}', {len(produtos)} resultados")

    def selecionar_linha(self, row, _):
        item = self.ui.tb_Produtos.item(row, 0)
        if item is None:
            return
        self.produto_selecionado_id = item.data(Qt.UserRole)
        produto = self.service.buscar_por_id(self.produto_selecionado_id)
        if produto:
            self.ui.txt_Codigo.setText(produto.codigo)
            self.ui.txt_Descricao.setText(produto.descricao)
            self.ui.txt_Peso.setValue(produto.peso)
            self.ui.txt_Custo.setValue(produto.custo)
            self._bloquear_campos()
            logger.debug(f"Linha selecionada: ID={produto.id}, row={row}")
