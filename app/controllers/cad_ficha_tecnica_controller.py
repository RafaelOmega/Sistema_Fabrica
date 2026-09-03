from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHeaderView,
    QMessageBox,
    QWidget,
)

from app.models.item_ficha_tecnica_table_model import (
    ItemFichaTecnicaTableModel,
)
from app.services.ficha_tecnica_service import FichaTecnicaService
from app.services.produto_service import ProdutoService
from app.utils.logger import get_logger
from app.views.ui_ficha_tecnica import Ui_Ficha_Tecnica

logger = get_logger("ficha_tecnica_controller")


class FichaTecnicaController(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Ficha_Tecnica()
        self.ui.setupUi(self)

        self.ficha_service = FichaTecnicaService()
        self.produto_service = ProdutoService()

        self.item_model = ItemFichaTecnicaTableModel()

        self.ficha_id = None
        self._produto_acabado_id = None
        self._materia_prima_atual_id = None
        self._item_edicao_row = None
        self._janela_produtos = None  # referência p/ evitar garbage collect

        self._configurar_tabela()
        self._configurar_campos()
        self._conectar_sinais()
        self._estado_inicial()

        logger.info("Tela de ficha técnica inicializada")

    # --- Configuração inicial ---

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

    def _configurar_campos(self):
        self.ui.txt_Descricao_Prod.setReadOnly(True)
        self.ui.txt_Total_Itens.setReadOnly(True)
        self.ui.txt_Total_Itens.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ui.txt_Total_Itens.setText("0,000")

    def _conectar_sinais(self):
        self.ui.bt_Pesquisa_Prod_Acabado.clicked.connect(
            self.abrir_pesquisa_produto_acabado)
        self.ui.bt_Novo.clicked.connect(self.abrir_cadastro_produto)
        self.ui.txt_Prod_Acabado.returnPressed.connect(self.abrir_ficha)
        self.ui.bt_Abrir_Ficha.clicked.connect(self.abrir_ficha)

        self.ui.bt_Pesquisa_Mat_Prima.clicked.connect(
            self.abrir_pesquisa_materia_prima)
        self.ui.txt_Cod_Mat_Prima.returnPressed.connect(
            self.pesquisar_materia_prima_direto)
        self.ui.bt_Salvar_Itens.clicked.connect(self.salvar_item)
        self.ui.bt_Limpar_Itens.clicked.connect(self.limpar_item)
        self.ui.bt_Excluir_Itens.clicked.connect(self.excluir_item)
        self.ui.bt_Sair_Ficha.clicked.connect(self.sair_ficha)

        self.ui.bt_Salvar.clicked.connect(self.salvar)
        self.ui.bt_Editar.clicked.connect(self.editar)
        self.ui.bt_Limpar.clicked.connect(self.limpar)
        self.ui.bt_Excluir.clicked.connect(self.excluir)

        self.ui.tb_Itens.selectionModel().selectionChanged.connect(
            self._ao_selecionar_item
        )

    def _atualizar_total(self):
        itens = self.item_model.obter_todos()
        total = sum(float(item.get("quantidade", 0) or 0) for item in itens)
        self.ui.txt_Total_Itens.setText(f"{total:.3f}".replace(".", ","))

    # --- Cabeçalho: produto acabado ---

    def abrir_pesquisa_produto_acabado(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )

        dialog = PesquisaProdutoController(self)
        if dialog.exec() == QDialog.Accepted:
            produto = dialog.produto_selecionado
            if not produto:
                return
            try:
                self.ficha_service.validar_produto_acabado(produto)
            except ValueError as e:
                QMessageBox.warning(self, "Aviso", str(e))
                return
            self.ui.txt_Prod_Acabado.setText(produto.codigo or "")
            self._abrir_ficha_do_produto(produto)

    def abrir_cadastro_produto(self):
        """Abre a tela de Cadastro de Produtos em janela independente,
        para permitir cadastrar rapidamente um novo produto acabado."""
        from app.controllers.cad_produtos_controller import (
            ProdutosController,
        )

        self._janela_produtos = ProdutosController()
        self._janela_produtos.setWindowTitle("Cadastro de Produtos")
        self._janela_produtos.setWindowFlag(Qt.Window, True)
        self._janela_produtos.show()
        logger.debug("Janela de cadastro de produtos aberta a partir "
                     "da ficha técnica")

    def abrir_ficha(self):
        codigo = self.ui.txt_Prod_Acabado.text().strip()
        if not codigo:
            QMessageBox.warning(
                self, "Aviso", "Informe ou pesquise o produto acabado."
            )
            return

        try:
            produto = self.produto_service.buscar_por_codigo(codigo)
            if not produto:
                QMessageBox.warning(self, "Aviso", "Produto não encontrado.")
                return

            self.ficha_service.validar_produto_acabado(produto)
            self._abrir_ficha_do_produto(produto)

        except ValueError as e:
            QMessageBox.warning(self, "Aviso", str(e))
        except Exception as e:
            logger.error(f"Erro ao abrir ficha técnica: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao abrir ficha: {e}")

    def _abrir_ficha_do_produto(self, produto):
        self._produto_acabado_id = produto.id

        try:
            ficha = self.ficha_service.buscar_por_produto_acabado(
                produto.id)
            if ficha:
                self._carregar_ficha(ficha.id)
            else:
                self._nova_ficha()
        except Exception as e:
            logger.error(
                f"Erro ao carregar ficha técnica: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao carregar: {e}")

    def _nova_ficha(self):
        self.ficha_id = None
        self.ui.txt_Sacos_Batida.clear()
        self._limpar_campos_item()
        self._limpar_itens()
        self._limpar_selecao_itens()
        self._atualizar_total()
        self._estado_edicao()
        self.ui.txt_Sacos_Batida.setFocus()
        logger.debug(
            f"Nova ficha técnica | produto_acabado_id="
            f"{self._produto_acabado_id}"
        )

    def _carregar_ficha(self, ficha_id):
        ficha, itens = self.ficha_service.buscar_com_itens(ficha_id)

        self.ficha_id = ficha.id
        self.ui.txt_Sacos_Batida.setText(str(ficha.sacos_por_batida or 0))

        self.item_model.atualizar_dados(itens)
        self._atualizar_total()
        self._estado_carregado()
        logger.info(f"Ficha técnica carregada | id={ficha.id}")

    # --- Itens: matéria-prima ---

    def abrir_pesquisa_materia_prima(self):
        from app.controllers.pesquisa_produto_controller import (
            PesquisaProdutoController,
        )

        dialog = PesquisaProdutoController(self)
        if dialog.exec() == QDialog.Accepted:
            produto = dialog.produto_selecionado
            if not produto:
                return
            try:
                self.ficha_service.validar_materia_prima(
                    produto, self._produto_acabado_id
                )
            except ValueError as e:
                QMessageBox.warning(self, "Aviso", str(e))
                return

            self._materia_prima_atual_id = produto.id
            self.ui.txt_Cod_Mat_Prima.setText(produto.codigo or "")
            self.ui.txt_Descricao_Prod.setText(produto.descricao or "")
            self.ui.txt_Qtde.setFocus()

    def pesquisar_materia_prima_direto(self):
        codigo = self.ui.txt_Cod_Mat_Prima.text().strip()
        if not codigo:
            return

        try:
            produto = self.produto_service.buscar_por_codigo(codigo)
            if not produto:
                QMessageBox.warning(
                    self, "Aviso", "Matéria-prima não encontrada."
                )
                self._limpar_campos_item()
                self.ui.txt_Cod_Mat_Prima.setFocus()
                self.ui.txt_Cod_Mat_Prima.selectAll()
                return

            self.ficha_service.validar_materia_prima(
                produto, self._produto_acabado_id
            )

            self._materia_prima_atual_id = produto.id
            self.ui.txt_Descricao_Prod.setText(produto.descricao or "")
            self.ui.txt_Qtde.setFocus()

        except ValueError as e:
            QMessageBox.warning(self, "Aviso", str(e))
            self._limpar_campos_item()
        except Exception as e:
            logger.error(
                f"Erro ao pesquisar matéria-prima: {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao pesquisar: {e}")

    def salvar_item(self):
        codigo = self.ui.txt_Cod_Mat_Prima.text().strip()
        descricao = self.ui.txt_Descricao_Prod.text().strip()
        qtde_text = self.ui.txt_Qtde.text().strip()

        if not codigo or not descricao or self._materia_prima_atual_id is None:
            QMessageBox.warning(
                self, "Aviso", "Pesquise uma matéria-prima primeiro."
            )
            return

        try:
            qtde = float(qtde_text.replace(",", "."))
            if qtde <= 0:
                raise ValueError("Quantidade deve ser maior que zero.")
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Quantidade inválida.")
            return

        # Impede matéria-prima duplicada na ficha (exceto o item
        # que está sendo editado no momento)
        itens_atuais = self.item_model.obter_todos()
        for row, item_existente in enumerate(itens_atuais):
            mesma_materia = (
                item_existente.get("materia_prima_id")
                == self._materia_prima_atual_id
            )
            editando_este_item = row == self._item_edicao_row
            if mesma_materia and not editando_este_item:
                QMessageBox.warning(
                    self, "Aviso",
                    "Esta matéria-prima já está na ficha. Selecione o "
                    "item na tabela para editar a quantidade."
                )
                return

        item = {
            "materia_prima_id": self._materia_prima_atual_id,
            "codigo": codigo,
            "descricao": descricao,
            "quantidade": qtde,
        }

        if self._item_edicao_row is not None:
            item_atual = self.item_model.obter_item(self._item_edicao_row)
            if item_atual and item_atual.get("id") is not None:
                item["id"] = item_atual["id"]
            self.item_model.atualizar_item(self._item_edicao_row, item)
            logger.debug(f"Item atualizado | row={self._item_edicao_row}")
        else:
            self.item_model.adicionar_item(item)
            logger.debug("Item adicionado à tabela")

        self._limpar_campos_item()
        self._limpar_selecao_itens()
        self._item_edicao_row = None
        self._atualizar_total()
        self.ui.txt_Cod_Mat_Prima.setFocus()

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

    def sair_ficha(self):
        """Cancela a ficha em edição (nova ou existente) sem salvar
        e retorna a tela ao estado inicial."""
        itens = self.item_model.obter_todos()
        if itens or self.ui.txt_Sacos_Batida.text().strip():
            resposta = QMessageBox.question(
                self,
                "Confirmar saída",
                "Existem dados não salvos nesta ficha. "
                "Deseja realmente sair sem salvar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if resposta != QMessageBox.StandardButton.Yes:
                return

        self._resetar_tela()
        logger.debug("Edição de ficha técnica cancelada (Sair Ficha)")

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
        self._materia_prima_atual_id = item.get("materia_prima_id")
        self.ui.txt_Cod_Mat_Prima.setText(item.get("codigo", ""))
        self.ui.txt_Descricao_Prod.setText(item.get("descricao", ""))
        self.ui.txt_Qtde.setText(
            str(item.get("quantidade", "")).replace(".", ",")
        )

        logger.debug(f"Item selecionado | row={row}")

    # --- Cabeçalho: CRUD da ficha ---

    def salvar(self):
        if self._produto_acabado_id is None:
            QMessageBox.warning(
                self, "Aviso", "Nenhum produto acabado selecionado."
            )
            return

        sacos_text = self.ui.txt_Sacos_Batida.text().strip()
        itens = self.item_model.obter_todos()

        try:
            self.ficha_service.salvar(
                produto_acabado_id=self._produto_acabado_id,
                sacos_por_batida=sacos_text,
                itens_data=itens,
                ficha_id=self.ficha_id,
            )

            logger.info(
                f"Ficha técnica salva | produto_acabado_id="
                f"{self._produto_acabado_id} | itens={len(itens)}"
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
                f"Erro inesperado ao salvar ficha técnica: {e}",
                exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    def editar(self):
        if self.ficha_id is None:
            QMessageBox.warning(
                self, "Aviso", "Nenhuma ficha técnica carregada."
            )
            return

        self._estado_edicao()
        self.ui.txt_Sacos_Batida.setFocus()
        logger.debug(f"Modo edição | ficha_id={self.ficha_id}")

    def limpar(self):
        self._resetar_tela()

    def excluir(self):
        if self.ficha_id is None:
            QMessageBox.warning(
                self, "Aviso", "Nenhuma ficha técnica carregada."
            )
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Deseja realmente excluir esta ficha técnica e todos "
            "os seus itens?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.ficha_service.excluir(self.ficha_id)
            logger.info(f"Ficha técnica excluída | id={self.ficha_id}")
            QMessageBox.information(
                self, "Sucesso", "Ficha técnica excluída com sucesso."
            )
            self._resetar_tela()

        except ValueError as e:
            logger.warning(f"Falha ao excluir ficha técnica: {e}")
            QMessageBox.warning(self, "Aviso", str(e))

        except Exception as e:
            logger.error(
                f"Erro inesperado ao excluir ficha técnica: {e}",
                exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")

    # --- Limpeza ---

    def _limpar_campos_item(self):
        self.ui.txt_Cod_Mat_Prima.clear()
        self.ui.txt_Descricao_Prod.clear()
        self.ui.txt_Qtde.clear()
        self._materia_prima_atual_id = None

    def _limpar_itens(self):
        self.item_model.limpar()

    def _limpar_selecao_itens(self):
        self.ui.tb_Itens.clearSelection()

    def _resetar_tela(self):
        self.ficha_id = None
        self._produto_acabado_id = None
        self._item_edicao_row = None

        self.ui.txt_Prod_Acabado.clear()
        self.ui.txt_Sacos_Batida.clear()
        self._limpar_campos_item()
        self._limpar_itens()
        self._limpar_selecao_itens()
        self._atualizar_total()

        self._estado_inicial()

    # --- Estados ---

    def _habilitar_cabecalho(self, habilitar):
        self.ui.txt_Sacos_Batida.setEnabled(habilitar)

    def _habilitar_itens(self, habilitar):
        self.ui.txt_Cod_Mat_Prima.setEnabled(habilitar)
        self.ui.bt_Pesquisa_Mat_Prima.setEnabled(habilitar)
        self.ui.txt_Qtde.setEnabled(habilitar)
        self.ui.bt_Salvar_Itens.setEnabled(habilitar)
        self.ui.bt_Limpar_Itens.setEnabled(habilitar)
        self.ui.bt_Excluir_Itens.setEnabled(habilitar)
        self.ui.bt_Sair_Ficha.setEnabled(habilitar)

    def _habilitar_busca_produto_acabado(self, habilitar):
        self.ui.txt_Prod_Acabado.setEnabled(habilitar)
        self.ui.bt_Pesquisa_Prod_Acabado.setEnabled(habilitar)
        self.ui.bt_Novo.setEnabled(habilitar)
        self.ui.bt_Abrir_Ficha.setEnabled(habilitar)

    def _estado_inicial(self):
        self._habilitar_busca_produto_acabado(True)
        self._habilitar_cabecalho(False)
        self._habilitar_itens(False)
        self.ui.tb_Itens.setEnabled(False)

        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)

    def _estado_edicao(self):
        """Usado tanto para uma ficha nova quanto para editar uma
        ficha já existente (self.ficha_id define qual é o caso)."""
        self._habilitar_busca_produto_acabado(False)
        self._habilitar_cabecalho(True)
        self._habilitar_itens(True)
        self.ui.tb_Itens.setEnabled(True)

        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(self.ficha_id is not None)

    def _estado_carregado(self):
        self._habilitar_busca_produto_acabado(True)
        self._habilitar_cabecalho(False)
        self._habilitar_itens(False)
        self.ui.tb_Itens.setEnabled(True)

        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
