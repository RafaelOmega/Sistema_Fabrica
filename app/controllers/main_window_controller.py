from datetime import datetime

from PySide6.QtCore import QDate, Qt, QTime, QTimer
from PySide6.QtWidgets import QMainWindow, QMdiSubWindow

from app.utils.logger import get_logger
from app.views.ui_main_window import Ui_MainWindow

logger = get_logger("main_window_controller")


class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Controle de Fábrica")

        self._iniciar_relogio()
        self._conectar_sinais()
        logger.info("MainWindow inicializada")

    def _iniciar_relogio(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._atualizar_relogio)
        self.timer.start(1000)
        self._atualizar_relogio()

    def _atualizar_relogio(self):
        agora = datetime.now()
        self.ui.dt_Data_Atual.setDate(
            QDate(agora.year, agora.month, agora.day))
        self.ui.dt_Hora_Atual.setTime(
            QTime(agora.hour, agora.minute, agora.second))

    def _conectar_sinais(self):
        self.ui.actionProdutos.triggered.connect(self.abrir_produtos)

    def _abrir_subjanela(self, classe_controller, titulo):
        """Abre (ou foca, se já aberta) uma tela de cadastro dentro do MDI.

        Reutilize este método para cada novo cadastro (Clientes, Pedidos,
        etc.) em vez de duplicar a lógica de verificação/abertura de janela.
        """
        for sub in self.ui.mdiArea.subWindowList():
            widget = sub.widget()
            if widget is not None and isinstance(widget, classe_controller):
                self.ui.mdiArea.setActiveSubWindow(sub)
                logger.debug(f"Janela '{titulo}' já estava aberta - focando")
                return

        sub = QMdiSubWindow()
        sub.setWidget(classe_controller())
        sub.setWindowTitle(titulo)
        sub.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.ui.mdiArea.addSubWindow(sub)
        sub.showMaximized()
        logger.info(f"Janela '{titulo}' aberta no MDI")

    def abrir_produtos(self):
        from app.controllers.cad_produtos_controller import ProdutosController
        self._abrir_subjanela(ProdutosController, "Cadastro de Produtos")
