from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMessageBox,
    QWidget,
)

from app.models.motivo_entrada_filter_proxy_model import (
    MotivoEntradaFilterProxyModel,
)
from app.models.motivo_entrada_table_model import MotivoEntradaTableModel
from app.services.motivo_entrada_service import MotivoEntradaService
from app.utils.logger import get_logger
from app.views.ui_motivo_entrada import Ui_Motivo_Entrada

logger = get_logger("motivo_entrada_controller")


class MotivoEntradaController(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Motivo_Entrada()
        self.ui.setupUi(self)

        self.service = MotivoEntradaService()
        self.model = MotivoEntradaTableModel()
        self.proxy_model = MotivoEntradaFilterProxyModel(self)

        self.motivo_selecionado_id = None

        self._configurar_tabela()
        self._conectar_sinais()
        self._carregar_dados()
        self._estado_inicial()

        logger.info("Tela de motivo de entrada inicializada")

    def _configurar_tabela(self):
        self.proxy_model.setSourceModel(self.model)

        self.ui.tb_Motivo_Entrada.setModel(self.proxy_model)
        self.ui.tb_Motivo_Entrada.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        self.ui.tb_Motivo_Entrada.setSelectionMode(
            QAbstractItemView.SingleSelection)
        self.ui.tb_Motivo_Entrada.setEditTriggers(
            QAbstractItemView.NoEditTriggers)
        self.ui.tb_Motivo_Entrada.setAlternatingRowColors(True)
        self.ui.tb_Motivo_Entrada.setSortingEnabled(True)
        self.ui.tb_Motivo_Entrada.verticalHeader().setVisible(False)

        header = self.ui.tb_Motivo_Entrada.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.ui.tb_Motivo_Entrada.sortByColumn(1, Qt.AscendingOrder)

    def _conectar_sinais(self):
        self.ui.bt_Novo.clicked.connect(self.novo)
        self.ui.bt_Salvar.clicked.connect(self.salvar)
        self.ui.bt_Editar.clicked.connect(self.editar)
        self.ui.bt_Limpar.clicked.connect(self.limpar)
        self.ui.bt_Excluir.clicked.connect(self.excluir)
        self.ui.bt_Pesquisar.clicked.connect(self.aplicar_filtro)
        self.ui.txt_Pesquisar.textChanged.connect(self.aplicar_filtro)

        self.ui.tb_Motivo_Entrada.selectionModel().selectionChanged.connect(
            self._ao_selecionar_linha
        )

    def _carregar_dados(self):
        try:
            motivos = self.service.listar_todos()
            self.model.atualizar_dados(motivos)
            self._limpar_selecao_tabela()
            logger.debug(
                f"Tabela carregada com {len(motivos)} motivos de entrada")
        except Exception as e:
            logger.error(
                f"Erro ao carregar motivos de entrada: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Erro", f"Erro ao carregar motivos de entrada: {e}")

    def aplicar_filtro(self):
        texto = self.ui.txt_Pesquisar.text().strip()
        self.proxy_model.definir_filtro(texto)

        self.motivo_selecionado_id = None
        self._limpar_selecao_tabela()
        self._limpar_campos()
        self._estado_inicial()

    def novo(self):
        self.motivo_selecionado_id = None
        self._limpar_selecao_tabela()
        self._estado_novo()

        try:
            proximo_codigo = self.service.obter_proximo_codigo()
            self.ui.txt_Codigo.setText(proximo_codigo)
        except Exception as e:
            logger.error(f"Erro ao gerar próximo código: {e}", exc_info=True)
            self.ui.txt_Codigo.clear()

        self.ui.txt_Descricao.setFocus()
        logger.debug("Modo novo motivo de entrada ativado")

    def salvar(self):
        codigo = self.ui.txt_Codigo.text().strip()
        descricao = self.ui.txt_Descricao.text().strip()

        try:
            self.service.salvar(
                codigo=codigo,
                descricao=descricao,
                motivo_id=self.motivo_selecionado_id,
            )

            logger.info(
                f"Motivo de entrada salvo com sucesso | "
                f"id={self.motivo_selecionado_id} | codigo={codigo}"
            )

            QMessageBox.information(
                self, "Sucesso", "Motivo de entrada salvo com sucesso.")
            self._resetar_tela()

        except ValueError as e:
            logger.warning(
                f"Falha de validação ao salvar motivo de entrada: {e}")
            QMessageBox.warning(self, "Aviso", str(e))

        except Exception as e:
            logger.error(
                f"Erro inesperado ao salvar motivo de entrada: {e}",
                exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    def editar(self):
        if self.motivo_selecionado_id is None:
            QMessageBox.warning(
                self, "Aviso", "Selecione um motivo de entrada na tabela.")
            return

        self._estado_edicao()
        self.ui.txt_Descricao.setFocus()
        logger.debug(
            f"Modo edição ativado | id={self.motivo_selecionado_id}")

    def limpar(self):
        self._resetar_tela()

    def excluir(self):
        if self.motivo_selecionado_id is None:
            QMessageBox.warning(
                self, "Aviso", "Selecione um motivo de entrada na tabela.")
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Deseja realmente excluir este motivo de entrada?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.service.excluir(self.motivo_selecionado_id)

            logger.info(
                f"Motivo de entrada excluído com sucesso | "
                f"id={self.motivo_selecionado_id}")

            QMessageBox.information(
                self, "Sucesso", "Motivo de entrada excluído com sucesso.")
            self._resetar_tela()

        except ValueError as e:
            logger.warning(f"Falha ao excluir motivo de entrada: {e}")
            QMessageBox.warning(self, "Aviso", str(e))

        except Exception as e:
            logger.error(
                f"Erro inesperado ao excluir motivo de entrada: {e}",
                exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    def _ao_selecionar_linha(self, selected, deselected):
        indexes_proxy = (
            self.ui.tb_Motivo_Entrada.selectionModel().selectedRows())

        if not indexes_proxy:
            return

        index_proxy = indexes_proxy[0]
        index_source = self.proxy_model.mapToSource(index_proxy)

        motivo = self.model.obter_motivo(index_source.row())
        if motivo is None:
            return

        self.motivo_selecionado_id = motivo.id
        self._preencher_campos(motivo)
        self._estado_linha_selecionada()

        logger.debug(
            f"Motivo de entrada selecionado | id={motivo.id} | "
            f"row_proxy={index_proxy.row()} | row_source={index_source.row()}"
        )

    def _preencher_campos(self, motivo):
        self.ui.txt_Codigo.setText(
            "" if motivo.codigo is None else str(motivo.codigo))
        self.ui.txt_Descricao.setText(
            "" if motivo.descricao is None else str(motivo.descricao))

    def _limpar_campos(self):
        self.ui.txt_Codigo.clear()
        self.ui.txt_Descricao.clear()

    def _limpar_selecao_tabela(self):
        self.ui.tb_Motivo_Entrada.clearSelection()

    def _habilitar_campos(self, habilitar):
        self.ui.txt_Descricao.setEnabled(habilitar)
        # Código é sempre desabilitado (automático)
        self.ui.txt_Codigo.setEnabled(False)

    def _estado_inicial(self):
        """Tudo bloqueado, exceto bt_Novo e pesquisa."""
        self._habilitar_campos(False)

        self.ui.bt_Novo.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)

        self.ui.txt_Pesquisar.setEnabled(True)
        self.ui.bt_Pesquisar.setEnabled(True)

    def _estado_novo(self):
        """Campos desbloqueados para cadastro novo (código automático)."""
        self._habilitar_campos(True)

        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)

        self.ui.txt_Pesquisar.setEnabled(True)
        self.ui.bt_Pesquisar.setEnabled(True)

    def _estado_linha_selecionada(self):
        """Linha selecionada: campos bloqueados, Editar/Excluir ativos."""
        self._habilitar_campos(False)

        self.ui.bt_Novo.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)

        self.ui.txt_Pesquisar.setEnabled(True)
        self.ui.bt_Pesquisar.setEnabled(True)

    def _estado_edicao(self):
        """Campos desbloqueados para editar existente (código travado)."""
        self._habilitar_campos(True)

        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)

        self.ui.txt_Pesquisar.setEnabled(True)
        self.ui.bt_Pesquisar.setEnabled(True)

    def _resetar_tela(self):
        self.motivo_selecionado_id = None

        self._limpar_campos()
        self.ui.txt_Pesquisar.clear()
        self._limpar_selecao_tabela()

        self._carregar_dados()
        self.proxy_model.definir_filtro("")
        self._estado_inicial()
