from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from app.utils.logger import get_logger
from app.views.ui_carregamento import Ui_Carregamento

logger = get_logger("carregamento_controller")


class CarregamentoController(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Carregamento()
        self.ui.setupUi(self)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.ui.progressBar.setRange(0, 0)

        logger.info("Tela de carregamento criada")

    def mostrar(self):
        self.show()

    def fechar(self):
        self.close()
        logger.info("Tela de carregamento fechada")
