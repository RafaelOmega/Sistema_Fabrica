from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
    QWidget,
)

from app.models.item_saida_table_model import ItemSaidaTableModel
from app.services.produto_service import ProdutoService
from app.services.saida_service import SaidaService
from app.utils.logger import get_logger
from app.utils.table_utils import configurar_tabela
from app.views.ui_saida import Ui_Saida

logger = get_logger("saida_controller")


class SaidaController(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Saida()
        self.ui.setupUi(self)

        self.saida_service = SaidaService()
        self.produto_service = ProdutoService()

        self.item_model = ItemSaidaTableModel()

        self.saida_id = None
        self._produto_atual_id = None
        self._item_edicao_row = None

        self._configurar_tabela()
        self._configurar_campos()
        self._conectar_sinais()
        self._estado_inicial()

        logger.info("Tela de saída de mercadorias inicializada")

    def _configurar_tabela(self):
        self.ui.tb_Itens.setModel(self.item_model)
        configurar_tabela(self.ui.tb_Itens, coluna_stretch=1)

    def _configurar_campos(self):
        self.ui.dt_Saida.setCalendarPopup(True)
        self.ui.dt_Saida.setDisplayFormat("dd/MM/yyyy")
        self.ui.txt_Descricao_Prod.setReadOnly(True)
        self.ui.txt_Total_Itens.setReadOnly(True)
        self.ui.txt_Total_Itens.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ui.txt_Total_Itens.setText("R$ 0,00")

    def _conectar_sinais(self):
        self.ui.bt_Novo.clicked.connect(self.novo)
        self.ui.bt_Pesquisa_Saida.clicked.connect(self.abrir_pesquisa_saida)
        self.ui.txt_Sequencia.returnPressed.connect(
            self.pesquisar_saida_direto)
        self.ui.bt_Abrir_Itens.clicked.connect(self.abrir_itens)
        self.ui.bt_Pesquisa_Itens.clicked.connect(self.abrir_pesquisa_produto)
        self.ui.txt_Cod_Prod.returnPressed.connect(
            self.pesquisar_produto_direto)
        self.ui.bt_Salvar_Itens.clicked.connect(self.salvar_item)
        self.ui.bt_Limpar_Itens.clicked.connect(self.limpar_item)
        self.ui.bt_Excluir_Itens.clicked.connect(self.excluir_item)
        self.ui.bt_Sair_Itens.clicked.connect(self.sair_itens)
        self.ui.bt_Salvar.clicked.connect(self.salvar)
        self.ui.bt_Editar.clicked.connect(self.editar)
        self.ui.bt_Limpar.clicked.connect(self.limpar)
        self.ui.bt_Excluir.clicked.connect(self.excluir)

        self.ui.tb_Itens.selectionModel().selectionChanged.connect(
            self._ao_selecionar_item
        )

    def _atualizar_total(self):
        itens = self.item_model.obter_todos()
        total = 0.0
        for item in itens:
            qtde = float(item.get("quantidade", 0) or 0)
            custo = float(item.get("custo", 0) or 0)
            total += qtde * custo
        self.ui.txt_Total_Itens.setText(f"R$ {total:.2f}".replace(".", ","))

    # --- Cabeçalho ---

    def novo(self):
        self.saida_id = None
        self._limpar_campos()
        self._limpar_itens()
        self._limpar_selecao_itens()
        self._atualizar_total()

        try:
            proxima = self.saida_service.obter_proxima_sequencia()
            self.ui.txt_Sequencia.setText(proxima)
        except Exception as e:
            logger.error(f"Erro ao gerar sequência: {e}", exc_info=True)

        self.ui.dt_Saida.setDate(QDate.currentDate())
        self._estado_novo()
        self.ui.dt_Saida.setFocus()
        logger.debug("Modo nova saída ativado")

    def abrir_pesquisa_saida(self):
        from app.controllers.pesquisa_saida_controller import (
            PesquisaSaidaController,
        )

        dialog = PesquisaSaidaController(self)
        if dialog.exec() == QDialog.Accepted:
            saida = dialog.saida_selecionada
            if saida:
                self._carregar_saida(saida["id"])

    def pesquisar_saida_direto(self):
        sequencia = self.ui.txt_Sequencia.text().strip()
        if not sequencia:
            return

        try:
            saida = self.saida_service.buscar_por_sequencia(sequencia)
            if not saida:
                QMessageBox.warning(self, "Aviso", "Saída não encontrada.")
                return
            self._carregar_saida(saida.id)
        except Exception as e:
            logger.error(f"Erro ao pesquisar saída: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao pesquisar: {e}")

    def _carregar_saida(self, saida_id):
        try:
            saida, itens = self.saida_service.buscar_com_itens(saida_id)

            self.saida_id = saida.id
            self.ui.txt_Sequencia.setText(saida.sequencia or "")
            self.ui.dt_Saida.setDate(
                QDate(
                    saida.data_saida.year,
                    saida.data_saida.month,
                    saida.data_saida.day,
                )
            )

            self.item_model.atualizar_dados(itens)
            self._atualizar_total()
            self._estado_carregado()
            logger.info(f"Saída carregada | id={saida.id}")
        except Exception as e:
            logger.error(f"Erro ao carregar saída: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao carregar: {e}")

    def salvar(self):
        if self.ui.bt_Sair_Itens.isEnabled():
            QMessageBox.warning(
                self, "Aviso", "Clique em Sair Itens antes de continuar."
            )
            return

        sequencia = self.ui.txt_Sequencia.text().strip()
        data_saida = self.ui.dt_Saida.date().toPython()
        itens = self.item_model.obter_todos()

        try:
            self.saida_service.salvar(
                sequencia=sequencia,
                data_saida=data_saida,
                itens_data=itens,
                saida_id=self.saida_id,
            )

            logger.info(
                f"Saída salva | id={self.saida_id} | "
                f"sequencia={sequencia} | itens={len(itens)}"
            )

            QMessageBox.information(
                self, "Sucesso", "Saída salva com sucesso."
            )
            self._resetar_tela()

        except ValueError as e:
            logger.warning(f"Falha de validação ao salvar saída: {e}")
            QMessageBox.warning(self, "Aviso", str(e))

        except Exception as e:
            logger.error(
                f"Erro inesperado ao salvar saída: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    def editar(self):
        if self.ui.bt_Sair_Itens.isEnabled():
            QMessageBox.warning(
                self, "Aviso", "Clique em Sair Itens antes de continuar."
            )
            return

        if self.saida_id is None:
            QMessageBox.warning(self, "Aviso", "Nenhuma saída carregada.")
            return

        self._estado_edicao()
        self.ui.dt_Saida.setFocus()
        logger.debug(f"Modo edição | id={self.saida_id}")

    def limpar(self):
        self._resetar_tela()

    def excluir(self):
        if self.ui.bt_Sair_Itens.isEnabled():
            QMessageBox.warning(
                self, "Aviso", "Clique em Sair Itens antes de continuar."
            )
            return

        if self.saida_id is None:
            QMessageBox.warning(self, "Aviso", "Nenhuma saída carregada.")
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Deseja realmente excluir esta saída e todos os seus itens?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.saida_service.excluir(self.saida_id)
            logger.info(f"Saída excluída | id={self.saida_id}")
            QMessageBox.information(
                self, "Sucesso", "Saída excluída com sucesso."
            )
            self._resetar_tela()

        except ValueError as e:
            logger.warning(f"Falha ao excluir saída: {e}")
            QMessageBox.warning(self, "Aviso", str(e))

        except Exception as e:
            logger.error(
                f"Erro inesperado ao excluir saída: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    # --- Itens ---

    def abrir_itens(self):
        self._estado_itens()
        self.ui.txt_Cod_Prod.setFocus()
        logger.debug("Seção de itens aberta")

    def sair_itens(self):
        self._limpar_campos_item()
        self._limpar_selecao_itens()
        self._item_edicao_row = None
        if self.saida_id is None:
            self._estado_novo()
        else:
            self._estado_edicao()
        logger.debug("Seção de itens fechada")

    def abrir_pesquisa_produto(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )

        dialog = PesquisaProdutoController(self)
        if dialog.exec() == QDialog.Accepted:
            produto = dialog.produto_selecionado
            if produto:
                self._produto_atual_id = produto.id
                self.ui.txt_Cod_Prod.setText(produto.codigo or "")
                self.ui.txt_Descricao_Prod.setText(produto.descricao or "")
                custo = getattr(produto, "custo", 0) or 0
                self.ui.txt_Custo.setText(f"{custo:.2f}".replace(".", ","))
                self.ui.txt_Qtde.setFocus()
                logger.debug(
                    f"Produto selecionado do dialog: {produto.codigo}"
                )

    def pesquisar_produto_direto(self):
        codigo = self.ui.txt_Cod_Prod.text().strip()
        if not codigo:
            return

        try:
            produto = self.produto_service.buscar_por_codigo(codigo)
            if produto:
                self._produto_atual_id = produto.id
                self.ui.txt_Descricao_Prod.setText(produto.descricao or "")
                custo = getattr(produto, "custo", 0) or 0
                self.ui.txt_Custo.setText(f"{custo:.2f}".replace(".", ","))
                self.ui.txt_Qtde.setFocus()
                logger.debug(f"Produto encontrado: {produto.codigo}")
            else:
                QMessageBox.warning(self, "Aviso", "Produto não encontrado.")
                self.ui.txt_Descricao_Prod.clear()
                self.ui.txt_Custo.clear()
                self._produto_atual_id = None
                self.ui.txt_Cod_Prod.setFocus()
                self.ui.txt_Cod_Prod.selectAll()
        except Exception as e:
            logger.error(f"Erro ao pesquisar produto: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao pesquisar: {e}")

    def salvar_item(self):
        codigo = self.ui.txt_Cod_Prod.text().strip()
        descricao = self.ui.txt_Descricao_Prod.text().strip()
        qtde_text = self.ui.txt_Qtde.text().strip()
        custo_text = self.ui.txt_Custo.text().strip()

        if not codigo or not descricao or self._produto_atual_id is None:
            QMessageBox.warning(
                self, "Aviso", "Pesquise um produto primeiro."
            )
            return

        try:
            qtde = float(qtde_text.replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Quantidade inválida.")
            return
        if qtde <= 0:
            QMessageBox.warning(
                self, "Aviso", "Quantidade deve ser maior que zero."
            )
            return

        try:
            custo = float(custo_text.replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Custo inválido.")
            return
        if custo < 0:
            QMessageBox.warning(
                self, "Aviso", "Custo não pode ser negativo."
            )
            return

        item = {
            "produto_id": self._produto_atual_id,
            "codigo": codigo,
            "descricao": descricao,
            "quantidade": qtde,
            "custo": custo,
        }

        if self._item_edicao_row is not None:
            self.item_model.atualizar_item(self._item_edicao_row, item)
            logger.debug(f"Item atualizado | row={self._item_edicao_row}")
        else:
            self.item_model.adicionar_item(item)
            logger.debug("Item adicionado à tabela")

        self._limpar_campos_item()
        self._limpar_selecao_itens()
        self._item_edicao_row = None
        self._atualizar_total()
        self.ui.txt_Cod_Prod.setFocus()

    def limpar_item(self):
        self._limpar_campos_item()
        self._limpar_selecao_itens()
        self._item_edicao_row = None

    def excluir_item(self):
        indexes = self.ui.tb_Itens.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(
                self, "Aviso", "Selecione um item na tabela."
            )
            return

        row = indexes[0].row()
        self.item_model.remover_item(row)
        self._limpar_campos_item()
        self._limpar_selecao_itens()
        self._item_edicao_row = None
        self._atualizar_total()
        logger.debug(f"Item removido | row={row}")

    def _ao_selecionar_item(self, selected, deselected):
        indexes = self.ui.tb_Itens.selectionModel().selectedRows()
        if not indexes:
            self._item_edicao_row = None
            return

        row = indexes[0].row()
        item = self.item_model.obter_item(row)
        if item is None:
            return

        self._item_edicao_row = row
        self._produto_atual_id = item.get("produto_id")
        self.ui.txt_Cod_Prod.setText(item.get("codigo", ""))
        self.ui.txt_Descricao_Prod.setText(item.get("descricao", ""))
        self.ui.txt_Qtde.setText(
            str(item.get("quantidade", "")).replace(".", ",")
        )
        self.ui.txt_Custo.setText(
            str(item.get("custo", "")).replace(".", ",")
        )

        logger.debug(f"Item selecionado | row={row}")

    # --- Limpeza ---

    def _limpar_campos(self):
        self.ui.txt_Sequencia.clear()
        self.ui.dt_Saida.setDate(QDate.currentDate())
        self._limpar_campos_item()

    def _limpar_campos_item(self):
        self.ui.txt_Cod_Prod.clear()
        self.ui.txt_Descricao_Prod.clear()
        self.ui.txt_Qtde.clear()
        self.ui.txt_Custo.clear()
        self._produto_atual_id = None

    def _limpar_itens(self):
        self.item_model.limpar()

    def _limpar_selecao_itens(self):
        self.ui.tb_Itens.clearSelection()

    # --- Estados ---

    def _habilitar_cabecalho(self, habilitar):
        self.ui.dt_Saida.setEnabled(habilitar)
        self.ui.bt_Abrir_Itens.setEnabled(habilitar)

    def _habilitar_itens(self, habilitar):
        self.ui.txt_Cod_Prod.setEnabled(habilitar)
        self.ui.bt_Pesquisa_Itens.setEnabled(habilitar)
        self.ui.txt_Qtde.setEnabled(habilitar)
        self.ui.txt_Custo.setEnabled(habilitar)
        self.ui.bt_Salvar_Itens.setEnabled(habilitar)
        self.ui.bt_Limpar_Itens.setEnabled(habilitar)
        self.ui.bt_Excluir_Itens.setEnabled(habilitar)
        self.ui.bt_Sair_Itens.setEnabled(habilitar)

    def _estado_inicial(self):
        self.ui.txt_Sequencia.setEnabled(True)
        self.ui.bt_Pesquisa_Saida.setEnabled(True)
        self._habilitar_cabecalho(False)
        self._habilitar_itens(False)
        self.ui.tb_Itens.setEnabled(False)

        self.ui.bt_Novo.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)

    def _estado_novo(self):
        self.ui.txt_Sequencia.setEnabled(False)
        self.ui.bt_Pesquisa_Saida.setEnabled(False)
        self._habilitar_cabecalho(True)
        self._habilitar_itens(False)
        self.ui.tb_Itens.setEnabled(True)

        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(False)

    def _estado_itens(self):
        self.ui.txt_Sequencia.setEnabled(False)
        self.ui.bt_Pesquisa_Saida.setEnabled(False)
        self._habilitar_cabecalho(False)
        self._habilitar_itens(True)
        self.ui.tb_Itens.setEnabled(True)

        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(False)

    def _estado_carregado(self):
        self.ui.txt_Sequencia.setEnabled(True)
        self.ui.bt_Pesquisa_Saida.setEnabled(True)
        self._habilitar_cabecalho(False)
        self._habilitar_itens(False)
        self.ui.tb_Itens.setEnabled(True)

        self.ui.bt_Novo.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)

    def _estado_edicao(self):
        self.ui.txt_Sequencia.setEnabled(False)
        self.ui.bt_Pesquisa_Saida.setEnabled(False)
        self._habilitar_cabecalho(True)
        self._habilitar_itens(False)
        self.ui.tb_Itens.setEnabled(True)

        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)

    def _resetar_tela(self):
        self.saida_id = None
        self._item_edicao_row = None
        self._produto_atual_id = None

        self._limpar_campos()
        self._limpar_itens()
        self._limpar_selecao_itens()
        self._atualizar_total()

        self._estado_inicial()
