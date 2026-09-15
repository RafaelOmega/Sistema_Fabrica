from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
    QWidget,
)

from app.models.ficha_tecnica_table_model import (
    FichaTecnicaTableModel,
    FichaTecnicaUnitarioTableModel,
)
from app.services.ficha_tecnica_service import FichaTecnicaService
from app.services.produto_service import ProdutoService
from app.utils.logger import get_logger
from app.utils.table_utils import configurar_tabela
from app.views.ui_ficha_tecnica import Ui_Ficha_Tecnica

logger = get_logger("ficha_tecnica_controller")


class FichaTecnicaController(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Ficha_Tecnica()
        self.ui.setupUi(self)

        self.ficha_service = FichaTecnicaService()
        self.produto_service = ProdutoService()

        self.item_model = FichaTecnicaTableModel()
        self.item_unitario_model = FichaTecnicaUnitarioTableModel()

        self.ficha_id = None
        self._produto_acabado_id = None
        self._produto_item_id = None
        self._item_edicao_row = None
        self._item_edicao_id = None

        self._configurar_tabelas()
        self._configurar_campos()
        self._conectar_sinais()
        self._estado_inicial()

        logger.info("Tela de ficha técnica inicializada")

    # --- Configuração ---

    def _configurar_tabelas(self):
        # Tabela Batida (editável via seleção)
        self.ui.tb_Itens_Batida.setModel(self.item_model)
        configurar_tabela(self.ui.tb_Itens_Batida, coluna_stretch=1)

        # Tabela Unitário (read-only, sem seleção)
        self.ui.tb_Itens_Unitario.setModel(self.item_unitario_model)
        configurar_tabela(
            self.ui.tb_Itens_Unitario,
            coluna_stretch=1,
            selecionavel=False,
        )

    def _configurar_campos(self):
        self.ui.txt_Descricao_Prod.setReadOnly(True)
        self.ui.txt_Total_Batida.setReadOnly(True)
        self.ui.txt_Total_Saco.setReadOnly(True)
        self.ui.txt_Total_Batida.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        self.ui.txt_Total_Saco.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        self.ui.txt_Total_Batida.setText("0,000")
        self.ui.txt_Total_Saco.setText("0,000000")

    def _conectar_sinais(self):
        self.ui.bt_Novo.clicked.connect(self.novo)
        self.ui.bt_Pesquisa_Prod_Acabado.clicked.connect(
            self.abrir_pesquisa_produto_acabado
        )
        self.ui.txt_Prod_Acabado.returnPressed.connect(
            self.pesquisar_produto_acabado_direto
        )
        self.ui.txt_Sacos_Batida.textChanged.connect(
            self._on_sacos_changed
        )
        self.ui.bt_Abrir_Ficha.clicked.connect(self.abrir_ficha)
        self.ui.bt_Pesquisa_Mat_Prima.clicked.connect(
            self.abrir_pesquisa_mat_prima
        )
        self.ui.txt_Cod_Mat_Prima.returnPressed.connect(
            self.pesquisar_mat_prima_direto
        )
        self.ui.bt_Salvar_Itens.clicked.connect(self.salvar_item)
        self.ui.bt_Limpar_Itens.clicked.connect(self.limpar_item)
        self.ui.bt_Excluir_Itens.clicked.connect(self.excluir_item)
        self.ui.bt_Sair_Ficha.clicked.connect(self.sair_ficha)
        self.ui.bt_Salvar.clicked.connect(self.salvar)
        self.ui.bt_Editar.clicked.connect(self.editar)
        self.ui.bt_Limpar.clicked.connect(self.limpar)
        self.ui.bt_Excluir.clicked.connect(self.excluir)

        self.ui.tb_Itens_Batida.selectionModel().selectionChanged.connect(
            self._ao_selecionar_item
        )

    # --- Totais e cálculo unitário ---

    def _get_sacos_batida(self):
        """Retorna sacos_batida como int (positivo), ou 0 se inválido.

        Sacos por batida é sempre um número inteiro — não existe meio
        saco — e a coluna no banco (fichas_tecnicas.sacos_batida) é
        Integer. Antes este método aceitava valores decimais (via
        float + replace(",", ".")) para o cálculo em tempo real, o que
        divergia da validação feita ao abrir os itens/salvar (que exige
        inteiro). Agora o parsing é único e consistente em toda a tela.
        """
        text = self.ui.txt_Sacos_Batida.text().strip()
        try:
            valor = int(text)
            return valor if valor > 0 else 0
        except (ValueError, TypeError):
            return 0

    def _atualizar_total_batida(self):
        itens = self.item_model.obter_todos()
        total = sum(
            float(item.get("quantidade_kg", 0) or 0) for item in itens
        )
        self.ui.txt_Total_Batida.setText(
            f"{total:.3f}".replace(".", ",")
        )

    def _atualizar_total_saco(self):
        itens = self.item_model.obter_todos()
        total_batida = sum(
            float(item.get("quantidade_kg", 0) or 0) for item in itens
        )
        sacos = self._get_sacos_batida()
        total_saco = total_batida / sacos if sacos > 0 else 0.0
        self.ui.txt_Total_Saco.setText(
            f"{total_saco:.6f}".replace(".", ",")
        )

    def _recalcular_unitario(self):
        """Recalcula a tabela unitária dividindo kg total pelos sacos."""
        sacos = self._get_sacos_batida()
        itens_batida = self.item_model.obter_todos()
        itens_unitario = []

        for item in itens_batida:
            kg_total = float(item.get("quantidade_kg", 0) or 0)
            kg_saco = kg_total / sacos if sacos > 0 else 0.0
            itens_unitario.append({
                "codigo": item.get("codigo", ""),
                "descricao": item.get("descricao", ""),
                "quantidade_kg": kg_saco,
            })

        self.item_unitario_model.atualizar_dados(itens_unitario)

    def _atualizar_totais(self):
        """Atualiza todos os totais + recalcula unitário."""
        self._atualizar_total_batida()
        self._recalcular_unitario()
        self._atualizar_total_saco()

    def _on_sacos_changed(self):
        """Chamado quando txt_Sacos_Batida muda."""
        self._recalcular_unitario()
        self._atualizar_total_saco()

    # --- Cabeçalho ---

    def novo(self):
        self.ficha_id = None
        self._produto_acabado_id = None
        self._item_edicao_row = None
        self._item_edicao_id = None
        self._limpar_campos()
        self._limpar_itens()
        self._limpar_selecao_itens()
        self._atualizar_totais()
        self._estado_novo()
        self.ui.txt_Prod_Acabado.setFocus()
        logger.debug("Modo nova ficha técnica ativado")

    def abrir_pesquisa_produto_acabado(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )

        dialog = PesquisaProdutoController(self)
        if dialog.exec() == QDialog.Accepted:
            produto = dialog.produto_selecionado
            if produto:
                if not getattr(produto, "prod_acabado", False):
                    QMessageBox.warning(
                        self,
                        "Aviso",
                        "Este produto não é um produto acabado.",
                    )
                    return
                self._produto_acabado_id = produto.id
                self.ui.txt_Prod_Acabado.setText(produto.codigo or "")
                self.ui.txt_Sacos_Batida.setFocus()
                logger.debug(
                    f"Produto acabado selecionado: {produto.codigo}"
                )

    def pesquisar_produto_acabado_direto(self):
        codigo = self.ui.txt_Prod_Acabado.text().strip()
        if not codigo:
            return

        try:
            produto = self.produto_service.buscar_por_codigo(codigo)
            if produto:
                if not getattr(produto, "prod_acabado", False):
                    QMessageBox.warning(
                        self,
                        "Aviso",
                        "Este produto não é um produto acabado.",
                    )
                    return
                self._produto_acabado_id = produto.id

                # Tenta carregar ficha existente
                ficha = self.ficha_service.buscar_por_produto(
                    produto.id
                )
                if ficha:
                    self._carregar_ficha(ficha.id)
                else:
                    QMessageBox.information(
                        self,
                        "Aviso",
                        "Nenhuma ficha técnica encontrada para "
                        "este produto.",
                    )
            else:
                QMessageBox.warning(
                    self, "Aviso", "Produto não encontrado."
                )
                self._produto_acabado_id = None
                self.ui.txt_Prod_Acabado.setFocus()
                self.ui.txt_Prod_Acabado.selectAll()
        except Exception as e:
            logger.error(
                f"Erro ao pesquisar produto: {e}", exc_info=True
            )
            QMessageBox.critical(
                self, "Erro", f"Erro ao pesquisar: {e}"
            )

    def abrir_ficha(self):
        """No estado inicial/carregado: carrega ficha existente.
        No estado novo/edição: abre seção de itens."""
        if self._produto_acabado_id is None:
            codigo = self.ui.txt_Prod_Acabado.text().strip()
            if not codigo:
                QMessageBox.warning(
                    self,
                    "Aviso",
                    "Selecione um produto acabado primeiro.",
                )
                return

            try:
                produto = self.produto_service.buscar_por_codigo(codigo)
                if not produto:
                    QMessageBox.warning(
                        self, "Aviso", "Produto não encontrado."
                    )
                    return
                if not getattr(produto, "prod_acabado", False):
                    QMessageBox.warning(
                        self,
                        "Aviso",
                        "Este produto não é um produto acabado.",
                    )
                    return
                self._produto_acabado_id = produto.id
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro", f"Erro ao pesquisar: {e}"
                )
                return

        # Estado inicial ou carregado → buscar ficha existente
        if self.ui.bt_Novo.isEnabled() and not self.ui.bt_Salvar.isEnabled():
            ficha = self.ficha_service.buscar_por_produto(
                self._produto_acabado_id
            )
            if ficha:
                self._carregar_ficha(ficha.id)
            else:
                QMessageBox.information(
                    self,
                    "Aviso",
                    "Nenhuma ficha técnica encontrada para "
                    "este produto.",
                )
            return

        # Estado novo ou edição → valida sacos antes de abrir itens
        sacos_text = self.ui.txt_Sacos_Batida.text().strip()
        if not sacos_text:
            QMessageBox.warning(
                self,
                "Aviso",
                "Informe a quantidade de sacos por batida.",
            )
            self.ui.txt_Sacos_Batida.setFocus()
            return

        # Reaproveita o mesmo parser usado no cálculo em tempo real
        # (_get_sacos_batida), garantindo que "abrir itens" e o
        # recálculo de totais concordem sobre o que é um valor válido.
        sacos = self._get_sacos_batida()
        if sacos <= 0:
            QMessageBox.warning(
                self, "Aviso", "Quantidade de sacos inválida."
            )
            return

        self._estado_ficha_aberta()
        self.ui.txt_Cod_Mat_Prima.setFocus()
        logger.debug("Seção de itens aberta")

    def _carregar_ficha(self, ficha_id):
        try:
            ficha, itens = self.ficha_service.buscar_com_itens(
                ficha_id
            )

            self.ficha_id = ficha.id
            self._produto_acabado_id = ficha.produto_id

            # Carregar código do produto acabado
            produto = self.produto_service.buscar_por_id(
                ficha.produto_id
            )
            if produto:
                self.ui.txt_Prod_Acabado.setText(produto.codigo or "")

            # Carregar itens na tabela batida PRIMEIRO
            self.item_model.atualizar_dados(itens)

            # Setar sacos_batida (dispara _on_sacos_changed →
            # recalcula unitário automaticamente)
            self.ui.txt_Sacos_Batida.setText(
                str(ficha.sacos_batida or "")
            )

            # Atualizar total da batida
            self._atualizar_total_batida()

            self._estado_carregado()
            logger.info(f"Ficha técnica carregada | id={ficha.id}")
        except Exception as e:
            logger.error(
                f"Erro ao carregar ficha: {e}", exc_info=True
            )
            QMessageBox.critical(
                self, "Erro", f"Erro ao carregar: {e}"
            )

    def salvar(self):
        if self.ui.bt_Sair_Ficha.isEnabled():
            QMessageBox.warning(
                self,
                "Aviso",
                "Clique em Sair Ficha antes de continuar.",
            )
            return

        produto_id = self._produto_acabado_id
        codigo_produto = self.ui.txt_Prod_Acabado.text().strip()
        sacos_batida = self.ui.txt_Sacos_Batida.text().strip()
        itens = self.item_model.obter_todos()

        try:
            self.ficha_service.salvar(
                produto_id=produto_id,
                codigo_produto=codigo_produto,
                sacos_batida=sacos_batida,
                itens_data=itens,
                ficha_id=self.ficha_id,
            )

            logger.info(
                f"Ficha técnica salva | id={self.ficha_id} | "
                f"produto_id={produto_id} | codigo={codigo_produto} | "
                f"itens={len(itens)}"
            )

            QMessageBox.information(
                self, "Sucesso", "Ficha técnica salva com sucesso."
            )
            self._resetar_tela()

        except ValueError as e:
            logger.warning(f"Falha de validação ao salvar ficha: {e}")
            QMessageBox.warning(self, "Aviso", str(e))

        except Exception as e:
            logger.error(
                f"Erro inesperado ao salvar ficha: {e}",
                exc_info=True,
            )
            QMessageBox.critical(
                self, "Erro", f"Erro inesperado: {e}"
            )

    def editar(self):
        if self.ui.bt_Sair_Ficha.isEnabled():
            QMessageBox.warning(
                self,
                "Aviso",
                "Clique em Sair Ficha antes de continuar.",
            )
            return

        if self.ficha_id is None:
            QMessageBox.warning(
                self, "Aviso", "Nenhuma ficha carregada."
            )
            return

        self._estado_edicao()
        self.ui.txt_Sacos_Batida.setFocus()
        logger.debug(f"Modo edição | id={self.ficha_id}")

    def limpar(self):
        self._resetar_tela()

    def excluir(self):
        if self.ui.bt_Sair_Ficha.isEnabled():
            QMessageBox.warning(
                self,
                "Aviso",
                "Clique em Sair Ficha antes de continuar.",
            )
            return

        if self.ficha_id is None:
            QMessageBox.warning(
                self, "Aviso", "Nenhuma ficha carregada."
            )
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Deseja realmente excluir esta ficha técnica "
            "e todos os seus itens?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.ficha_service.excluir(self.ficha_id)
            logger.info(
                f"Ficha técnica excluída | id={self.ficha_id}"
            )
            QMessageBox.information(
                self, "Sucesso", "Ficha técnica excluída com sucesso."
            )
            self._resetar_tela()

        except ValueError as e:
            logger.warning(f"Falha ao excluir ficha: {e}")
            QMessageBox.warning(self, "Aviso", str(e))

        except Exception as e:
            logger.error(
                f"Erro inesperado ao excluir ficha: {e}",
                exc_info=True,
            )
            QMessageBox.critical(
                self, "Erro", f"Erro inesperado: {e}"
            )

    # --- Itens ---

    def sair_ficha(self):
        self._limpar_campos_item()
        self._limpar_selecao_itens()
        self._item_edicao_row = None
        self._item_edicao_id = None
        if self.ficha_id is None:
            self._estado_novo()
        else:
            self._estado_edicao()
        logger.debug("Seção de itens fechada")

    def abrir_pesquisa_mat_prima(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )

        dialog = PesquisaProdutoController(self)
        if dialog.exec() == QDialog.Accepted:
            produto = dialog.produto_selecionado
            if produto:
                if not getattr(produto, "mat_prima", False):
                    QMessageBox.warning(
                        self,
                        "Aviso",
                        "Este produto não é uma matéria prima.",
                    )
                    return
                self._produto_item_id = produto.id
                self.ui.txt_Cod_Mat_Prima.setText(produto.codigo or "")
                self.ui.txt_Descricao_Prod.setText(
                    produto.descricao or ""
                )
                self.ui.txt_Qtde.setFocus()
                logger.debug(
                    f"Matéria prima selecionada: {produto.codigo}"
                )

    def pesquisar_mat_prima_direto(self):
        codigo = self.ui.txt_Cod_Mat_Prima.text().strip()
        if not codigo:
            return

        try:
            produto = self.produto_service.buscar_por_codigo(codigo)
            if produto:
                if not getattr(produto, "mat_prima", False):
                    QMessageBox.warning(
                        self,
                        "Aviso",
                        "Este produto não é uma matéria prima.",
                    )
                    return
                self._produto_item_id = produto.id
                self.ui.txt_Descricao_Prod.setText(
                    produto.descricao or ""
                )
                self.ui.txt_Qtde.setFocus()
                logger.debug(
                    f"Matéria prima encontrada: {produto.codigo}"
                )
            else:
                QMessageBox.warning(
                    self, "Aviso", "Produto não encontrado."
                )
                self.ui.txt_Descricao_Prod.clear()
                self._produto_item_id = None
                self.ui.txt_Cod_Mat_Prima.setFocus()
                self.ui.txt_Cod_Mat_Prima.selectAll()
        except Exception as e:
            logger.error(
                f"Erro ao pesquisar matéria prima: {e}",
                exc_info=True,
            )
            QMessageBox.critical(
                self, "Erro", f"Erro ao pesquisar: {e}"
            )

    def salvar_item(self):
        codigo = self.ui.txt_Cod_Mat_Prima.text().strip()
        descricao = self.ui.txt_Descricao_Prod.text().strip()
        qtde_text = self.ui.txt_Qtde.text().strip()

        if not codigo or not descricao or self._produto_item_id is None:
            QMessageBox.warning(
                self, "Aviso", "Pesquise uma matéria prima primeiro."
            )
            return

        try:
            qtde = float(qtde_text.replace(",", "."))
            if qtde <= 0:
                raise ValueError("Quantidade deve ser maior que zero.")
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Quantidade inválida.")
            return

        item = {
            "produto_id": self._produto_item_id,
            "codigo_produto": codigo,
            "codigo": codigo,
            "descricao": descricao,
            "quantidade_kg": qtde,
        }

        if self._item_edicao_row is not None:
            # Preserva o id original do item (quando ele já existe no
            # banco). Sem isso, o item editado perde seu id e o
            # FichaTecnicaRepository._salvar_com_itens_inner trata a
            # edição como "excluir o item antigo + inserir um novo",
            # em vez de fazer um update in-place.
            if self._item_edicao_id is not None:
                item["id"] = self._item_edicao_id
            self.item_model.atualizar_item(
                self._item_edicao_row, item
            )
            logger.debug(
                f"Item atualizado | row={self._item_edicao_row} | "
                f"id={self._item_edicao_id}"
            )
        else:
            self.item_model.adicionar_item(item)
            logger.debug("Item adicionado à tabela")

        self._limpar_campos_item()
        self._limpar_selecao_itens()
        self._item_edicao_row = None
        self._item_edicao_id = None
        self._atualizar_totais()
        self.ui.txt_Cod_Mat_Prima.setFocus()

    def limpar_item(self):
        self._limpar_campos_item()
        self._limpar_selecao_itens()
        self._item_edicao_row = None
        self._item_edicao_id = None

    def excluir_item(self):
        indexes = self.ui.tb_Itens_Batida.selectionModel().selectedRows()
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
        self._item_edicao_id = None
        self._atualizar_totais()
        logger.debug(f"Item removido | row={row}")

    def _ao_selecionar_item(self, selected, deselected):
        indexes = self.ui.tb_Itens_Batida.selectionModel().selectedRows()
        if not indexes:
            self._item_edicao_row = None
            self._item_edicao_id = None
            return

        row = indexes[0].row()
        item = self.item_model.obter_item(row)
        if item is None:
            return

        self._item_edicao_row = row
        self._item_edicao_id = item.get("id")
        self._produto_item_id = item.get("produto_id")
        self.ui.txt_Cod_Mat_Prima.setText(item.get("codigo", ""))
        self.ui.txt_Descricao_Prod.setText(item.get("descricao", ""))
        self.ui.txt_Qtde.setText(
            str(item.get("quantidade_kg", "")).replace(".", ",")
        )

        logger.debug(f"Item selecionado | row={row}")

    # --- Limpeza ---

    def _limpar_campos(self):
        self.ui.txt_Prod_Acabado.clear()
        self.ui.txt_Sacos_Batida.clear()
        self._limpar_campos_item()

    def _limpar_campos_item(self):
        self.ui.txt_Cod_Mat_Prima.clear()
        self.ui.txt_Descricao_Prod.clear()
        self.ui.txt_Qtde.clear()
        self._produto_item_id = None

    def _limpar_itens(self):
        self.item_model.limpar()
        self.item_unitario_model.limpar()

    def _limpar_selecao_itens(self):
        self.ui.tb_Itens_Batida.clearSelection()

    # --- Estados ---

    def _habilitar_busca_ficha(self, habilitar):
        """Campos de busca/carregamento de ficha."""
        self.ui.txt_Prod_Acabado.setEnabled(habilitar)
        self.ui.bt_Pesquisa_Prod_Acabado.setEnabled(habilitar)
        self.ui.bt_Abrir_Ficha.setEnabled(habilitar)

    def _habilitar_cabecalho(self, habilitar):
        """Campo de edição do cabeçalho."""
        self.ui.txt_Sacos_Batida.setEnabled(habilitar)

    def _habilitar_itens(self, habilitar):
        self.ui.txt_Cod_Mat_Prima.setEnabled(habilitar)
        self.ui.bt_Pesquisa_Mat_Prima.setEnabled(habilitar)
        self.ui.txt_Qtde.setEnabled(habilitar)
        self.ui.bt_Salvar_Itens.setEnabled(habilitar)
        self.ui.bt_Limpar_Itens.setEnabled(habilitar)
        self.ui.bt_Excluir_Itens.setEnabled(habilitar)
        self.ui.bt_Sair_Ficha.setEnabled(habilitar)

    def _estado_inicial(self):
        self._habilitar_busca_ficha(True)
        self._habilitar_cabecalho(False)
        self._habilitar_itens(False)
        self.ui.tb_Itens_Batida.setEnabled(False)
        self.ui.tb_Itens_Unitario.setEnabled(False)

        self.ui.bt_Novo.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)

    def _estado_novo(self):
        self._habilitar_busca_ficha(True)
        self._habilitar_cabecalho(True)
        self._habilitar_itens(False)
        self.ui.tb_Itens_Batida.setEnabled(True)
        self.ui.tb_Itens_Unitario.setEnabled(True)

        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(False)

    def _estado_ficha_aberta(self):
        self._habilitar_busca_ficha(False)
        self._habilitar_cabecalho(False)
        self._habilitar_itens(True)
        self.ui.tb_Itens_Batida.setEnabled(True)
        self.ui.tb_Itens_Unitario.setEnabled(True)

        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(False)

    def _estado_carregado(self):
        self._habilitar_busca_ficha(True)
        self._habilitar_cabecalho(False)
        self._habilitar_itens(False)
        self.ui.tb_Itens_Batida.setEnabled(True)
        self.ui.tb_Itens_Unitario.setEnabled(True)

        self.ui.bt_Novo.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)

    def _estado_edicao(self):
        self._habilitar_busca_ficha(True)
        self._habilitar_cabecalho(True)
        self._habilitar_itens(False)
        self.ui.tb_Itens_Batida.setEnabled(True)
        self.ui.tb_Itens_Unitario.setEnabled(True)

        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)

    def _resetar_tela(self):
        self.ficha_id = None
        self._item_edicao_row = None
        self._item_edicao_id = None
        self._produto_acabado_id = None

        self._limpar_campos()
        self._limpar_itens()
        self._limpar_selecao_itens()
        self._atualizar_totais()

        self._estado_inicial()
