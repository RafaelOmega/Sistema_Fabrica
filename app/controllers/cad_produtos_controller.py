from decimal import Decimal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMessageBox,
    QWidget,
)
from app.models.produto_filter_proxy_model import ProdutoFilterProxyModel
from app.models.produto_table_model import ProdutoTableModel
from app.services.produto_service import ProdutoService
from app.utils.logger import get_logger
from app.utils.table_utils import configurar_tabela
from app.views.ui_produtos import Ui_Produtos

logger = get_logger("produtos_controller")


class ProdutosController(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Produtos()
        self.ui.setupUi(self)
        self.service = ProdutoService()
        self.model = ProdutoTableModel()
        self.proxy_model = ProdutoFilterProxyModel(self)
        self.produto_selecionado_id = None
        self._configurar_tabela()
        self._conectar_sinais()
        self._carregar_dados()
        self._estado_inicial()
        logger.info("Tela de produtos inicializada")

    def _configurar_tabela(self):
        self.proxy_model.setSourceModel(self.model)
        self.ui.tb_Produtos.setModel(self.proxy_model)
        configurar_tabela(
            self.ui.tb_Produtos, coluna_stretch=1, ordenavel=True
        )
        self.ui.tb_Produtos.sortByColumn(1, Qt.AscendingOrder)

    def _conectar_sinais(self):
        self.ui.bt_Novo.clicked.connect(self.novo)
        self.ui.bt_Salvar.clicked.connect(self.salvar)
        self.ui.bt_Editar.clicked.connect(self.editar)
        self.ui.bt_Limpar.clicked.connect(self.limpar)
        self.ui.bt_Excluir.clicked.connect(self.excluir)
        self.ui.bt_Pesquisar.clicked.connect(self.aplicar_filtro)
        self.ui.txt_Pesquisar.textChanged.connect(self.aplicar_filtro)
        self.ui.tb_Produtos.selectionModel().selectionChanged.connect(
            self._ao_selecionar_linha
        )

    def _carregar_dados(self):
        try:
            produtos = self.service.listar_todos()
            self.model.atualizar_dados(produtos)
            self._limpar_selecao_tabela()
            logger.debug(f"Tabela carregada com {len(produtos)} produtos")
        except Exception as e:
            logger.error(f"Erro ao carregar produtos: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Erro", f"Erro ao carregar produtos: {e}")

    def aplicar_filtro(self):
        texto = self.ui.txt_Pesquisar.text().strip()
        self.proxy_model.definir_filtro(texto)
        self.produto_selecionado_id = None
        self._limpar_selecao_tabela()
        self._limpar_campos()
        self._estado_inicial()

    def novo(self):
        self.produto_selecionado_id = None
        self._limpar_campos()
        self._limpar_selecao_tabela()
        self._estado_novo()
        self.ui.txt_Codigo.setFocus()
        logger.debug("Modo novo produto ativado")

    def salvar(self):
        codigo = self.ui.txt_Codigo.text().strip()
        descricao = self.ui.txt_Descricao.text().strip()
        peso = self.ui.txt_Peso.value()
        custo = Decimal(str(self.ui.txt_Custo.value()))
        prod_acabado = self.ui.ch_Prod_Acabado.isChecked()
        mat_prima = self.ui.ch_Mat_Prima.isChecked()
        mao_obra = self.ui.ch_Mao_Obra.isChecked()
        controla_estoque = self.ui.ch_Controla_Estoque.isChecked()
        try:
            self.service.salvar(
                codigo=codigo,
                descricao=descricao,
                peso=peso,
                custo=custo,
                produto_id=self.produto_selecionado_id,
                prod_acabado=prod_acabado,
                mat_prima=mat_prima,
                mao_obra=mao_obra,
                controla_estoque=controla_estoque,
            )
            logger.info(
                f"Produto salvo com sucesso | id={self.produto_selecionado_id} | codigo={codigo}"
            )
            QMessageBox.information(
                self, "Sucesso", "Produto salvo com sucesso.")
            self._resetar_tela()
        except ValueError as e:
            logger.warning(f"Falha de validação ao salvar produto: {e}")
            QMessageBox.warning(self, "Aviso", str(e))
        except Exception as e:
            logger.error(
                f"Erro inesperado ao salvar produto: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    def editar(self):
        if self.produto_selecionado_id is None:
            QMessageBox.warning(
                self, "Aviso", "Selecione um produto na tabela.")
            return
        self._estado_edicao()
        self.ui.txt_Codigo.setFocus()
        logger.debug(f"Modo edição ativado | id={self.produto_selecionado_id}")

    def limpar(self):
        self._resetar_tela()

    def excluir(self):
        if self.produto_selecionado_id is None:
            QMessageBox.warning(
                self, "Aviso", "Selecione um produto na tabela.")
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Deseja realmente excluir este produto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return
        try:
            self.service.excluir(self.produto_selecionado_id)
            logger.info(
                f"Produto excluído com sucesso | id={self.produto_selecionado_id}")
            QMessageBox.information(
                self, "Sucesso", "Produto excluído com sucesso.")
            self._resetar_tela()
        except ValueError as e:
            logger.warning(f"Falha ao excluir produto: {e}")
            QMessageBox.warning(self, "Aviso", str(e))
        except Exception as e:
            logger.error(
                f"Erro inesperado ao excluir produto: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    def _ao_selecionar_linha(self, selected, deselected):
        indexes_proxy = self.ui.tb_Produtos.selectionModel().selectedRows()
        if not indexes_proxy:
            return
        index_proxy = indexes_proxy[0]
        index_source = self.proxy_model.mapToSource(index_proxy)
        produto = self.model.obter_produto(index_source.row())
        if produto is None:
            return
        self.produto_selecionado_id = produto.id
        self._preencher_campos(produto)
        self._estado_linha_selecionada()
        logger.debug(
            f"Produto selecionado | id={produto.id} | row_proxy={index_proxy.row()} | row_source={index_source.row()}"
        )

    def _preencher_campos(self, produto):
        self.ui.txt_Codigo.setText(
            "" if produto.codigo is None else str(produto.codigo))
        self.ui.txt_Descricao.setText(
            "" if produto.descricao is None else str(produto.descricao))
        self.ui.txt_Peso.setValue(
            0.0 if produto.peso is None else float(produto.peso))
        self.ui.txt_Custo.setValue(
            0.0 if produto.custo is None else float(produto.custo))
        # Carrega checkboxes
        self.ui.ch_Prod_Acabado.setChecked(
            bool(getattr(produto, "prod_acabado", False)))
        self.ui.ch_Mat_Prima.setChecked(
            bool(getattr(produto, "mat_prima", False)))
        self.ui.ch_Mao_Obra.setChecked(
            bool(getattr(produto, "mao_obra", False)))
        self.ui.ch_Controla_Estoque.setChecked(
            bool(getattr(produto, "controla_estoque", False)))

    def _limpar_campos(self):
        self.ui.txt_Codigo.clear()
        self.ui.txt_Descricao.clear()
        self.ui.txt_Peso.setValue(0.0)
        self.ui.txt_Custo.setValue(0.0)
        # Limpa checkboxes
        self.ui.ch_Prod_Acabado.setChecked(False)
        self.ui.ch_Mat_Prima.setChecked(False)
        self.ui.ch_Mao_Obra.setChecked(False)
        self.ui.ch_Controla_Estoque.setChecked(False)

    def _limpar_selecao_tabela(self):
        self.ui.tb_Produtos.clearSelection()

    def _habilitar_campos_produto(self, habilitar):
        self.ui.txt_Codigo.setEnabled(habilitar)
        self.ui.txt_Descricao.setEnabled(habilitar)
        self.ui.txt_Peso.setEnabled(habilitar)
        self.ui.txt_Custo.setEnabled(habilitar)
        # Habilita/desabilita checkboxes junto com os campos
        self.ui.ch_Prod_Acabado.setEnabled(habilitar)
        self.ui.ch_Mat_Prima.setEnabled(habilitar)
        self.ui.ch_Mao_Obra.setEnabled(habilitar)
        self.ui.ch_Controla_Estoque.setEnabled(habilitar)

    def _estado_inicial(self):
        self._habilitar_campos_produto(False)
        self.ui.bt_Novo.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)
        self.ui.txt_Pesquisar.setEnabled(True)
        self.ui.bt_Pesquisar.setEnabled(True)

    def _estado_novo(self):
        self._habilitar_campos_produto(True)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.txt_Pesquisar.setEnabled(True)
        self.ui.bt_Pesquisar.setEnabled(True)

    def _estado_linha_selecionada(self):
        self._habilitar_campos_produto(False)
        self.ui.bt_Novo.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.txt_Pesquisar.setEnabled(True)
        self.ui.bt_Pesquisar.setEnabled(True)

    def _estado_edicao(self):
        self._habilitar_campos_produto(True)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.txt_Pesquisar.setEnabled(True)
        self.ui.bt_Pesquisar.setEnabled(True)

    def _resetar_tela(self):
        self.produto_selecionado_id = None
        self._limpar_campos()
        self.ui.txt_Pesquisar.clear()
        self._limpar_selecao_tabela()
        self._carregar_dados()
        self.proxy_model.definir_filtro("")
        self._estado_inicial()
