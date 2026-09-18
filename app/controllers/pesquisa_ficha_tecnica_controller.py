from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QMessageBox

from app.models.pesquisa_ficha_tecnica_table_model import (
    PesquisaFichaTecnicaTableModel,
)
from app.services.ficha_tecnica_service import FichaTecnicaService
from app.utils.logger import get_logger
from app.utils.table_utils import configurar_tabela
from app.views.ui_pesquisa_Ficha_Tecnica import Ui_Pesquisa_Fichas_Tecnicas

logger = get_logger("pesquisa_ficha_tecnica_controller")


class PesquisaFichaTecnicaController(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Pesquisa_Fichas_Tecnicas()
        self.ui.setupUi(self)

        self.ficha_service = FichaTecnicaService()
        self.model = PesquisaFichaTecnicaTableModel()

        self.ficha_selecionada = None
        self._todas_fichas = []

        self.ui.tb_Fichas_Tecnicas.setModel(self.model)
        configurar_tabela(self.ui.tb_Fichas_Tecnicas, coluna_stretch=1)

        self.ui.bt_Pesquisa.clicked.connect(self.confirmar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._filtrar)
        self.ui.tb_Fichas_Tecnicas.doubleClicked.connect(
            self._confirmar_por_duplo_clique
        )
        self.ui.tb_Fichas_Tecnicas.selectionModel().currentRowChanged.connect(
            self._ao_selecionar
        )

        self._carregar_fichas()

        logger.info("Tela de pesquisa de fichas técnicas inicializada")

    # --- Dados ---

    def _carregar_fichas(self):
        try:
            self._todas_fichas = self.ficha_service.listar_todos()
            self.model.atualizar_dados(self._todas_fichas)

            if not self._todas_fichas:
                QMessageBox.information(
                    self, "Aviso", "Nenhuma ficha técnica cadastrada."
                )
            logger.debug(
                f"{len(self._todas_fichas)} fichas técnicas carregadas"
            )
        except Exception as e:
            logger.error(
                f"Erro ao carregar fichas técnicas: {e}", exc_info=True
            )
            QMessageBox.critical(self, "Erro", f"Erro ao carregar: {e}")

    def _filtrar(self):
        """Filtra em memória por código ou descrição (ignora acentos
        na prática via casefold)."""
        filtro = self.ui.txt_Pesquisa.text().strip().lower()
        if not filtro:
            self.model.atualizar_dados(self._todas_fichas)
            return

        fichas = [
            f for f in self._todas_fichas
            if filtro in str(f.get("codigo", "")).lower()
            or filtro in str(f.get("descricao", "")).lower()
        ]
        self.model.atualizar_dados(fichas)

    # --- Seleção / confirmação ---

    def _ao_selecionar(self, current, previous):
        if current.isValid():
            self.ficha_selecionada = self.model.obter_ficha(
                current.row()
            )
        else:
            self.ficha_selecionada = None

    def _confirmar_por_duplo_clique(self, index):
        ficha = self.model.obter_ficha(index.row())
        if ficha:
            self.ficha_selecionada = ficha
        self.confirmar()

    def confirmar(self):
        if self.ficha_selecionada is None:
            QMessageBox.warning(
                self, "Aviso", "Selecione uma ficha técnica."
            )
            return

        logger.debug(
            f"Ficha selecionada | id={self.ficha_selecionada.get('id')}"
        )
        self.accept()
