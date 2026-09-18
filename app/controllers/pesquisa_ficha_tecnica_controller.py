from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
)

from app.models.ficha_tecnica_filter_proxy_model import (
    FichaTecnicaFilterProxyModel,
)
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

        self.service = FichaTecnicaService()
        self.model = PesquisaFichaTecnicaTableModel()
        self.proxy_model = FichaTecnicaFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.ficha_selecionada = None

        self._configurar_tabela()
        self._conectar_sinais()
        self._carregar_dados()

        logger.info("Tela de pesquisa de fichas técnicas inicializada")

    def _configurar_tabela(self):
        self.ui.tb_Fichas_Tecnicas.setModel(self.proxy_model)
        configurar_tabela(
            self.ui.tb_Fichas_Tecnicas, coluna_stretch=2, ordenavel=True
        )

    def _conectar_sinais(self):
        self.ui.txt_Pesquisa.textChanged.connect(self._aplicar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self.confirmar)
        self.ui.tb_Fichas_Tecnicas.doubleClicked.connect(self.confirmar)

    def _carregar_dados(self):
        try:
            fichas = self.service.listar_todos()
            self.model.atualizar_dados(fichas)

            if not fichas:
                QMessageBox.information(
                    self, "Aviso", "Nenhuma ficha técnica cadastrada."
                )
            logger.debug(f"{len(fichas)} fichas técnicas carregadas")
        except Exception as e:
            logger.error(
                f"Erro ao carregar fichas técnicas: {e}", exc_info=True
            )
            QMessageBox.critical(self, "Erro", f"Erro ao carregar: {e}")

    def _aplicar_filtro(self):
        texto = self.ui.txt_Pesquisa.text().strip()
        self.proxy_model.definir_filtro(texto)

    def confirmar(self):
        indexes = self.ui.tb_Fichas_Tecnicas.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(
                self, "Aviso", "Selecione uma ficha técnica."
            )
            return

        index_proxy = indexes[0]
        index_source = self.proxy_model.mapToSource(index_proxy)
        self.ficha_selecionada = self.model.obter_ficha(
            index_source.row()
        )

        if self.ficha_selecionada:
            logger.debug(
                f"Ficha selecionada: {self.ficha_selecionada.get('id')}"
            )
            self.accept()
