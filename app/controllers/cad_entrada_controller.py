from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHeaderView,
    QMessageBox,
    QWidget,
)

from app.models.item_entrada_table_model import ItemEntradaTableModel
from app.services.alteracao_custo_service import AlteracaoCustoService
from app.services.entrada_service import EntradaService
from app.services.motivo_entrada_service import MotivoEntradaService
from app.services.produto_service import ProdutoService
from app.utils.logger import get_logger
from app.views.ui_entrada import Ui_Entrada

logger = get_logger("entrada_controller")


class EntradaController(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Entrada()
        self.ui.setupUi(self)

        self.entrada_service = EntradaService()
        self.motivo_service = MotivoEntradaService()
        self.produto_service = ProdutoService()
        self.alteracao_custo_service = AlteracaoCustoService()

        self.item_model = ItemEntradaTableModel()

        self.entrada_id = None
        self._produto_atual_id = None
        self._item_edicao_row = None
        self._peso_produto = None
        # ← NOVO: acumula alterações para commit transacional
        self._alteracoes_custo = []
        self._produtos_custo_detectado = set()  # ← NOVO: evita duplicação de detecção

        self._configurar_tabela()
        self._configurar_campos()
        self._carregar_motivos()
        self._conectar_sinais()
        self._estado_inicial()

        logger.info("Tela de entrada de mercadorias inicializada")

    def _configurar_tabela(self):
        self.ui.tb_Itens.setModel(self.item_model)
        self.ui.tb_Itens.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tb_Itens.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tb_Itens.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tb_Itens.setAlternatingRowColors(True)
        self.ui.tb_Itens.verticalHeader().setVisible(False)

        header = self.ui.tb_Itens.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

    def _configurar_campos(self):
        self.ui.dt_Entrada.setCalendarPopup(True)
        self.ui.dt_Entrada.setDisplayFormat("dd/MM/yyyy")
        self.ui.txt_Descricao_Prod.setReadOnly(True)
        self.ui.txt_Total_Itens.setReadOnly(True)
        self.ui.txt_Total_Itens.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ui.txt_Total_Itens.setText("R$ 0,00")

        # Campos especiais — ocultos por padrão
        self.ui.lb_Milho.setVisible(False)
        self.ui.txt_Milho.setVisible(False)

    def _carregar_motivos(self):
        try:
            motivos = self.motivo_service.listar_todos()
            self.ui.cmb_Motivo.clear()
            self.ui.cmb_Motivo.addItem("Selecione...", None)
            for motivo in motivos:
                self.ui.cmb_Motivo.addItem(motivo.descricao, motivo.id)
        except Exception as e:
            logger.error(f"Erro ao carregar motivos: {e}", exc_info=True)

    def _conectar_sinais(self):
        self.ui.bt_Novo.clicked.connect(self.novo)
        self.ui.bt_Pesquisa_Entrada.clicked.connect(
            self.abrir_pesquisa_entrada)
        self.ui.txt_Sequencia.returnPressed.connect(
            self.pesquisar_entrada_direto)
        self.ui.bt_Abrir_Itens.clicked.connect(self.abrir_itens)
        self.ui.bt_Pesquisa_Itens.clicked.connect(self.abrir_pesquisa_produto)
        self.ui.txt_Cod_Prod.returnPressed.connect(
            self.pesquisar_produto_direto)
        self.ui.txt_Milho.editingFinished.connect(
            self._calcular_custo_especial)
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
        self.entrada_id = None
        self._alteracoes_custo = []              # ← LIMPA alterações pendentes
        self._produtos_custo_detectado = set()   # ← LIMPA controle de duplicação
        self._limpar_campos()
        self._limpar_itens()
        self._limpar_selecao_itens()
        self._atualizar_total()

        try:
            proxima = self.entrada_service.obter_proxima_sequencia()
            self.ui.txt_Sequencia.setText(proxima)
        except Exception as e:
            logger.error(f"Erro ao gerar sequência: {e}", exc_info=True)

        self.ui.dt_Entrada.setDate(QDate.currentDate())
        self._estado_novo()
        self.ui.dt_Entrada.setFocus()
        logger.debug("Modo nova entrada ativado")

    def abrir_pesquisa_entrada(self):
        from app.controllers.pesquisa_entrada_controller import (
            PesquisaEntradaController,
        )

        dialog = PesquisaEntradaController(self)
        if dialog.exec() == QDialog.Accepted:
            entrada = dialog.entrada_selecionada
            if entrada:
                self._carregar_entrada(entrada["id"])

    def pesquisar_entrada_direto(self):
        sequencia = self.ui.txt_Sequencia.text().strip()
        if not sequencia:
            return

        try:
            entrada = self.entrada_service.buscar_por_sequencia(sequencia)
            if not entrada:
                QMessageBox.warning(self, "Aviso", "Entrada não encontrada.")
                return
            self._carregar_entrada(entrada.id)
        except Exception as e:
            logger.error(f"Erro ao pesquisar entrada: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao pesquisar: {e}")

    def _carregar_entrada(self, entrada_id):
        try:
            entrada, itens = self.entrada_service.buscar_com_itens(entrada_id)

            self.entrada_id = entrada.id
            self._alteracoes_custo = []              # ← LIMPA ao carregar
            self._produtos_custo_detectado = set()   # ← LIMPA ao carregar
            self.ui.txt_Sequencia.setText(entrada.sequencia or "")
            self.ui.dt_Entrada.setDate(
                QDate(
                    entrada.data_entrada.year,
                    entrada.data_entrada.month,
                    entrada.data_entrada.day,
                )
            )

            motivo_id = entrada.motivo_entrada_id
            for i in range(self.ui.cmb_Motivo.count()):
                if self.ui.cmb_Motivo.itemData(i) == motivo_id:
                    self.ui.cmb_Motivo.setCurrentIndex(i)
                    break

            self.item_model.atualizar_dados(itens)
            self._atualizar_total()
            self._estado_carregado()
            logger.info(f"Entrada carregada | id={entrada.id}")
        except Exception as e:
            logger.error(f"Erro ao carregar entrada: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao carregar: {e}")

    def salvar(self):
        if self.ui.bt_Sair_Itens.isEnabled():
            QMessageBox.warning(
                self, "Aviso", "Clique em Sair Itens antes de continuar."
            )
            return

        sequencia = self.ui.txt_Sequencia.text().strip()
        data_entrada = self.ui.dt_Entrada.date().toPython()
        motivo_id = self.ui.cmb_Motivo.currentData()
        itens = self.item_model.obter_todos()

        try:
            # ← ALTERADO: usa salvar_com_alteracao_custo (transação única)
            self.entrada_service.salvar_com_alteracao_custo(
                sequencia=sequencia,
                data_entrada=data_entrada,
                motivo_id=motivo_id,
                itens_data=itens,
                entrada_id=self.entrada_id,
                alteracoes_custo=self._alteracoes_custo or None,
            )

            logger.info(
                f"Entrada salva | id={self.entrada_id} | "
                f"sequencia={sequencia} | itens={len(itens)}"
            )

            QMessageBox.information(
                self, "Sucesso", "Entrada salva com sucesso."
            )
            self._resetar_tela()

        except ValueError as e:
            logger.warning(f"Falha de validação ao salvar entrada: {e}")
            QMessageBox.warning(self, "Aviso", str(e))

        except Exception as e:
            logger.error(
                f"Erro inesperado ao salvar entrada: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    def editar(self):
        if self.ui.bt_Sair_Itens.isEnabled():
            QMessageBox.warning(
                self, "Aviso", "Clique em Sair Itens antes de continuar."
            )
            return

        if self.entrada_id is None:
            QMessageBox.warning(self, "Aviso", "Nenhuma entrada carregada.")
            return

        self._estado_edicao()
        self.ui.dt_Entrada.setFocus()
        logger.debug(f"Modo edição | id={self.entrada_id}")

    def limpar(self):
        self._resetar_tela()

    def excluir(self):
        if self.ui.bt_Sair_Itens.isEnabled():
            QMessageBox.warning(
                self, "Aviso", "Clique em Sair Itens antes de continuar."
            )
            return

        if self.entrada_id is None:
            QMessageBox.warning(self, "Aviso", "Nenhuma entrada carregada.")
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Deseja realmente excluir esta entrada e todos os seus itens?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.entrada_service.excluir(self.entrada_id)
            logger.info(f"Entrada excluída | id={self.entrada_id}")
            QMessageBox.information(
                self, "Sucesso", "Entrada excluída com sucesso."
            )
            self._resetar_tela()

        except ValueError as e:
            logger.warning(f"Falha ao excluir entrada: {e}")
            QMessageBox.warning(self, "Aviso", str(e))

        except Exception as e:
            logger.error(
                f"Erro inesperado ao excluir entrada: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    # --- Itens ---

    def abrir_itens(self):
        motivo_id = self.ui.cmb_Motivo.currentData()
        if not motivo_id:
            QMessageBox.warning(
                self, "Aviso", "Selecione um motivo de entrada primeiro."
            )
            self.ui.cmb_Motivo.setFocus()
            return

        self._estado_itens()
        self.ui.txt_Cod_Prod.setFocus()
        logger.debug("Seção de itens aberta")

    def sair_itens(self):
        self._limpar_campos_item()
        self._limpar_selecao_itens()
        self._item_edicao_row = None
        if self.entrada_id is None:
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
                self._peso_produto = getattr(produto, "peso", None)
                self._verificar_regra_produto(produto.codigo or "")
                # ← ALTERADO: usa regra do service em vez de CODIGO_MILHO
                regra = self.entrada_service.obter_regra_produto(
                    produto.codigo or "")
                if not regra:
                    custo = getattr(produto, "custo", 0) or 0
                    self.ui.txt_Custo.setText(f"{custo:.2f}".replace(".", ","))
                self.ui.cmb_Un.setFocus()
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
                self._peso_produto = getattr(produto, "peso", None)
                self._verificar_regra_produto(produto.codigo or "")
                # ← ALTERADO: usa regra do service em vez de CODIGO_MILHO
                regra = self.entrada_service.obter_regra_produto(
                    produto.codigo or "")
                if not regra:
                    custo = getattr(produto, "custo", 0) or 0
                    self.ui.txt_Custo.setText(f"{custo:.2f}".replace(".", ","))
                self.ui.cmb_Un.setFocus()
                logger.debug(f"Produto encontrado: {produto.codigo}")
            else:
                QMessageBox.warning(self, "Aviso", "Produto não encontrado.")
                self.ui.txt_Descricao_Prod.clear()
                self.ui.txt_Custo.clear()
                self._produto_atual_id = None
                self._peso_produto = None
                self._ocultar_campos_especiais()
                self.ui.txt_Cod_Prod.setFocus()
                self.ui.txt_Cod_Prod.selectAll()
        except Exception as e:
            logger.error(f"Erro ao pesquisar produto: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao pesquisar: {e}")

    # ← ALTERADO: _verificar_produto_milho → _verificar_regra_produto (usa service)
    def _verificar_regra_produto(self, codigo):
        """Exibe campos especiais se o produto tiver regra configurada no service."""
        regra = self.entrada_service.obter_regra_produto(codigo.strip())
        tem_regra = regra is not None

        if tem_regra:
            self.ui.lb_Milho.setVisible(True)
            self.ui.txt_Milho.setVisible(True)
            self.ui.txt_Milho.clear()
            self.ui.txt_Custo.clear()
            # Atualiza label com a descrição da regra
            if "descricao" in regra:
                self.ui.lb_Milho.setText(regra["descricao"])
            self.ui.txt_Milho.setFocus()
            logger.debug(f"Regra especial detectada: {codigo} - {regra}")
        else:
            self._ocultar_campos_especiais()

    # ← ALTERADO: _ocultar_milho → _ocultar_campos_especiais
    def _ocultar_campos_especiais(self):
        self.ui.lb_Milho.setVisible(False)
        self.ui.txt_Milho.setVisible(False)
        self.ui.txt_Milho.clear()

    # ← ALTERADO: _calcular_custo_milho → _calcular_custo_especial (usa divisor do service)
    def _calcular_custo_especial(self):
        """Calcula custo unitário dividindo o valor pelo divisor da regra."""
        valor_text = self.ui.txt_Milho.text().strip()
        if not valor_text:
            return

        codigo = self.ui.txt_Cod_Prod.text().strip()
        regra = self.entrada_service.obter_regra_produto(codigo)
        if not regra or "divisor_custo" not in regra:
            return

        try:
            valor = float(valor_text.replace(",", "."))
            divisor = float(regra["divisor_custo"])
            custo = valor / divisor
            self.ui.txt_Custo.setText(f"{custo:.4f}".replace(".", ","))
            logger.debug(
                f"Cálculo especial: {valor} / {divisor} = {custo:.4f}")
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Valor inválido.")

    # ← ALTERADO: _verificar_alteracao_custo → _detectar_alteracao_custo (não commita, apenas armazena)
    def _detectar_alteracao_custo(self, codigo, custo_novo):
        """Detecta alteração de custo e armazena para commit transacional posterior."""
        if self._produto_atual_id in self._produtos_custo_detectado:
            return  # Já detectado para este produto nesta sessão

        try:
            produto = self.produto_service.buscar_por_codigo(codigo)
            if not produto:
                return

            custo_cadastrado = float(getattr(produto, "custo", 0) or 0)

            if abs(custo_cadastrado - custo_novo) < 0.0001:
                return

            # Armazena para commit posterior na mesma transação do salvar()
            self._alteracoes_custo.append({
                "codigo_produto": codigo,
                "produto_id": produto.id,
                "custo_anterior": custo_cadastrado,
                "custo_atual": custo_novo,
            })
            self._produtos_custo_detectado.add(self._produto_atual_id)

            logger.info(
                f"Alteração de custo detectada | produto={codigo} | "
                f"de {custo_cadastrado:.4f} para {custo_novo:.4f}"
            )
        except Exception as e:
            logger.error(
                f"Erro ao detectar alteração de custo: {e}", exc_info=True
            )

    def salvar_item(self):
        codigo = self.ui.txt_Cod_Prod.text().strip()
        descricao = self.ui.txt_Descricao_Prod.text().strip()
        unidade = self.ui.cmb_Un.currentText()
        qtde_text = self.ui.txt_Qtde.text().strip()
        custo_text = self.ui.txt_Custo.text().strip()

        if not codigo or not descricao or self._produto_atual_id is None:
            QMessageBox.warning(
                self, "Aviso", "Pesquise um produto primeiro."
            )
            return

        if not unidade:
            QMessageBox.warning(self, "Aviso", "Selecione a unidade.")
            return

        try:
            qtde_digitada = float(qtde_text.replace(",", "."))
            if qtde_digitada <= 0:
                raise ValueError("Quantidade deve ser maior que zero.")
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Quantidade inválida.")
            return

        try:
            custo = float(custo_text.replace(",", "."))
            if custo < 0:
                raise ValueError("Custo não pode ser negativo.")
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Custo inválido.")
            return

        # Conversão KG: divide pelo peso do produto
        # SOMENTE na tabela, não altera txt_Qtde
        qtde_tabela = qtde_digitada
        if unidade.strip().upper() == "KG":
            if self._peso_produto is None or self._peso_produto <= 0:
                QMessageBox.warning(
                    self,
                    "Aviso",
                    "Produto sem peso cadastrado. Não é possível calcular por KG.",
                )
                return
            qtde_tabela = qtde_digitada / self._peso_produto
            logger.debug(
                f"Cálculo KG: {qtde_digitada} / {self._peso_produto} "
                f"= {qtde_tabela:.3f}"
            )

        # ← ALTERADO: detecta alteração de custo (armazena, não commita)
        self._detectar_alteracao_custo(codigo, custo)

        item = {
            "produto_id": self._produto_atual_id,
            "codigo": codigo,
            "descricao": descricao,
            "unidade": unidade,
            "quantidade": qtde_tabela,
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

        unidade = item.get("unidade", "")
        idx = self.ui.cmb_Un.findText(unidade)
        if idx >= 0:
            self.ui.cmb_Un.setCurrentIndex(idx)

        self.ui.txt_Qtde.setText(
            str(item.get("quantidade", "")).replace(".", ",")
        )
        self.ui.txt_Custo.setText(
            str(item.get("custo", "")).replace(".", ",")
        )

        self._verificar_regra_produto(item.get("codigo", ""))

        logger.debug(f"Item selecionado | row={row}")

    # --- Limpeza ---

    def _limpar_campos(self):
        self.ui.txt_Sequencia.clear()
        self.ui.dt_Entrada.setDate(QDate.currentDate())
        if self.ui.cmb_Motivo.count() > 0:
            self.ui.cmb_Motivo.setCurrentIndex(0)
        self._limpar_campos_item()

    def _limpar_campos_item(self):
        self.ui.txt_Cod_Prod.clear()
        self.ui.txt_Descricao_Prod.clear()
        self.ui.cmb_Un.setCurrentIndex(0)
        self.ui.txt_Qtde.clear()
        self.ui.txt_Custo.clear()
        self._produto_atual_id = None
        self._peso_produto = None
        self._ocultar_campos_especiais()

    def _limpar_itens(self):
        self.item_model.limpar()

    def _limpar_selecao_itens(self):
        self.ui.tb_Itens.clearSelection()

    # --- Estados ---

    def _habilitar_cabecalho(self, habilitar):
        self.ui.dt_Entrada.setEnabled(habilitar)
        self.ui.cmb_Motivo.setEnabled(habilitar)
        self.ui.bt_Abrir_Itens.setEnabled(habilitar)

    def _habilitar_itens(self, habilitar):
        self.ui.txt_Cod_Prod.setEnabled(habilitar)
        self.ui.bt_Pesquisa_Itens.setEnabled(habilitar)
        self.ui.cmb_Un.setEnabled(habilitar)
        self.ui.txt_Qtde.setEnabled(habilitar)
        self.ui.txt_Custo.setEnabled(habilitar)
        self.ui.bt_Salvar_Itens.setEnabled(habilitar)
        self.ui.bt_Limpar_Itens.setEnabled(habilitar)
        self.ui.bt_Excluir_Itens.setEnabled(habilitar)
        self.ui.bt_Sair_Itens.setEnabled(habilitar)

    def _estado_inicial(self):
        self.ui.txt_Sequencia.setEnabled(True)
        self.ui.bt_Pesquisa_Entrada.setEnabled(True)
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
        self.ui.bt_Pesquisa_Entrada.setEnabled(False)
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
        self.ui.bt_Pesquisa_Entrada.setEnabled(False)
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
        self.ui.bt_Pesquisa_Entrada.setEnabled(True)
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
        self.ui.bt_Pesquisa_Entrada.setEnabled(False)
        self._habilitar_cabecalho(True)
        self._habilitar_itens(False)
        self.ui.tb_Itens.setEnabled(True)

        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)

    def _resetar_tela(self):
        self.entrada_id = None
        self._item_edicao_row = None
        self._produto_atual_id = None
        self._peso_produto = None
        self._alteracoes_custo = []              # ← LIMPA alterações pendentes
        self._produtos_custo_detectado = set()   # ← LIMPA controle de duplicação

        self._limpar_campos()
        self._limpar_itens()
        self._limpar_selecao_itens()
        self._atualizar_total()

        self._estado_inicial()
