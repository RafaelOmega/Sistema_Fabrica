from decimal import Decimal

from PySide6.QtWidgets import QDialog, QMessageBox, QWidget

from app.services.produto_service import ProdutoService
from app.utils.logger import get_logger
from app.views.ui_produtos import Ui_Produtos

logger = get_logger("produtos_controller")

CASAS_DECIMAIS = 4


class ProdutosController(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Produtos()
        self.ui.setupUi(self)

        self.service = ProdutoService()
        self.produto_selecionado_id = None

        self._configurar_campos()
        self._conectar_sinais()
        self._estado_inicial()
        logger.info("Tela de produtos inicializada")

    # --- Configuração ---

    def _configurar_campos(self):
        self.ui.txt_Peso.setDecimals(CASAS_DECIMAIS)
        self.ui.txt_Custo.setDecimals(CASAS_DECIMAIS)

    def _conectar_sinais(self):
        self.ui.bt_Novo.clicked.connect(self.novo)
        self.ui.bt_Salvar.clicked.connect(self.salvar)
        self.ui.bt_Editar.clicked.connect(self.editar)
        self.ui.bt_Limpar.clicked.connect(self.limpar)
        self.ui.bt_Excluir.clicked.connect(self.excluir)
        self.ui.bt_Pesquisar_Produtos.clicked.connect(
            self.abrir_pesquisa_produtos)

    # --- Pesquisa (tela separada) ---

    def abrir_pesquisa_produtos(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )

        dialog = PesquisaProdutoController(self)
        if dialog.exec() != QDialog.Accepted:
            return
        produto = dialog.produto_selecionado
        if produto is None:
            return
        self.produto_selecionado_id = produto.id
        self._preencher_campos(produto)
        self._estado_linha_selecionada()
        logger.debug(f"Produto selecionado | id={produto.id}")

    # --- Ações ---

    def novo(self):
        self.produto_selecionado_id = None
        self._limpar_campos()
        self._estado_novo()
        self.ui.txt_Codigo.setFocus()
        logger.debug("Modo novo produto ativado")

    def salvar(self):
        codigo = self.ui.txt_Codigo.text().strip()
        descricao = self.ui.txt_Descricao.text().strip()
        peso = self.ui.txt_Peso.value()
        custo = Decimal(str(self.ui.txt_Custo.value())).quantize(
            Decimal("0.0001"))

        try:
            self.service.salvar(
                codigo=codigo,
                descricao=descricao,
                peso=peso,
                custo=custo,
                produto_id=self.produto_selecionado_id,
                prod_acabado=self.ui.ch_Prod_Acabado.isChecked(),
                mat_prima=self.ui.ch_Mat_Prima.isChecked(),
                mao_obra=self.ui.ch_Mao_Obra.isChecked(),
                controla_estoque=self.ui.ch_Controla_Estoque.isChecked(),
            )
            logger.info(
                f"Produto salvo | id={self.produto_selecionado_id} "
                f"| codigo={codigo}")
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
                self, "Aviso", "Pesquise e selecione um produto.")
            return
        self._estado_edicao()
        self.ui.txt_Codigo.setFocus()
        logger.debug(
            f"Modo edição ativado | id={self.produto_selecionado_id}")

    def limpar(self):
        self._resetar_tela()

    def excluir(self):
        if self.produto_selecionado_id is None:
            QMessageBox.warning(
                self, "Aviso", "Pesquise e selecione um produto.")
            return
        resposta = QMessageBox.question(
            self, "Confirmação",
            "Deseja realmente excluir este produto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return
        try:
            self.service.excluir(self.produto_selecionado_id)
            logger.info(
                f"Produto excluído | id={self.produto_selecionado_id}")
            self._resetar_tela()
        except ValueError as e:
            logger.warning(f"Falha ao excluir produto: {e}")
            QMessageBox.warning(self, "Aviso", str(e))
        except Exception as e:
            logger.error(
                f"Erro inesperado ao excluir produto: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    # --- Campos ---

    def _preencher_campos(self, produto):
        self.ui.txt_Codigo.setText(
            "" if produto.codigo is None else str(produto.codigo))
        self.ui.txt_Descricao.setText(
            "" if produto.descricao is None else str(produto.descricao))
        self.ui.txt_Peso.setValue(
            0.0 if produto.peso is None else float(produto.peso))
        self.ui.txt_Custo.setValue(
            0.0 if produto.custo is None else float(produto.custo))
        self.ui.ch_Prod_Acabado.setChecked(bool(produto.prod_acabado))
        self.ui.ch_Mat_Prima.setChecked(bool(produto.mat_prima))
        self.ui.ch_Mao_Obra.setChecked(bool(produto.mao_obra))
        self.ui.ch_Controla_Estoque.setChecked(bool(produto.controla_estoque))

    def _limpar_campos(self):
        self.ui.txt_Codigo.clear()
        self.ui.txt_Descricao.clear()
        self.ui.txt_Peso.setValue(0.0)
        self.ui.txt_Custo.setValue(0.0)
        self.ui.ch_Prod_Acabado.setChecked(False)
        self.ui.ch_Mat_Prima.setChecked(False)
        self.ui.ch_Mao_Obra.setChecked(False)
        self.ui.ch_Controla_Estoque.setChecked(False)

    def _habilitar_campos_produto(self, habilitar):
        self.ui.txt_Codigo.setEnabled(habilitar)
        self.ui.txt_Descricao.setEnabled(habilitar)
        self.ui.txt_Peso.setEnabled(habilitar)
        self.ui.txt_Custo.setEnabled(habilitar)
        self.ui.ch_Prod_Acabado.setEnabled(habilitar)
        self.ui.ch_Mat_Prima.setEnabled(habilitar)
        self.ui.ch_Mao_Obra.setEnabled(habilitar)
        self.ui.ch_Controla_Estoque.setEnabled(habilitar)

    # --- Estados (helper único) ---

    def _aplicar_estado(self, *, campos=False, novo=False, salvar=False,
                        editar=False, excluir=False, limpar=False):
        self._habilitar_campos_produto(campos)
        self.ui.bt_Novo.setEnabled(novo)
        self.ui.bt_Salvar.setEnabled(salvar)
        self.ui.bt_Editar.setEnabled(editar)
        self.ui.bt_Excluir.setEnabled(excluir)
        self.ui.bt_Limpar.setEnabled(limpar)

    def _estado_inicial(self):
        self._aplicar_estado()

    def _estado_novo(self):
        self._aplicar_estado(campos=True, salvar=True, limpar=True)

    def _estado_linha_selecionada(self):
        self._aplicar_estado(editar=True, excluir=True, limpar=True)

    def _estado_edicao(self):
        self._aplicar_estado(campos=True, salvar=True,
                             excluir=True, limpar=True)

    def _resetar_tela(self):
        self.produto_selecionado_id = None
        self._limpar_campos()
        self._estado_inicial()
