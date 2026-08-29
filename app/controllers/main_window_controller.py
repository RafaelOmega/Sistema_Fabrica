from datetime import datetime

from PySide6.QtCore import QDate, Qt, QTime, QTimer
from PySide6.QtWidgets import QMainWindow, QMdiSubWindow, QMessageBox

from app.utils.logger import get_logger
from app.views.ui_main_window import Ui_MainWindow

logger = get_logger("main_window_controller")


class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Controle de Fábrica")

        self._database_ready = False

        self._iniciar_relogio()
        self._conectar_sinais()
        self._configurar_estado_inicial()

        logger.info("MainWindow inicializada")

    def _configurar_estado_inicial(self):
        self.ui.actionProdutos.setEnabled(False)
        self.ui.actionMotivo_Entrada.setEnabled(False)

        if self.statusBar():
            self.statusBar().showMessage("Inicializando conexão com o banco...")

    def on_database_ready(self):
        self._database_ready = True
        self.ui.actionProdutos.setEnabled(True)
        self.ui.actionMotivo_Entrada.setEnabled(True)

        if self.statusBar():
            self.statusBar().showMessage("Pronto", 3000)

        logger.info("Banco pronto - menus liberados")

    def on_database_failed(self, error_message):
        self._database_ready = False
        self.ui.actionProdutos.setEnabled(False)
        self.ui.actionMotivo_Entrada.setEnabled(False)

        if self.statusBar():
            self.statusBar().showMessage("Falha ao conectar no banco")

        logger.error(
            f"Falha informada para a janela principal: {error_message}")

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
        self.ui.actionMotivo_Entrada.triggered.connect(
            self.abrir_motivos_entrada)

    def _abrir_subjanela(self, classe_controller, titulo):
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
        if not self._database_ready:
            QMessageBox.information(
                self,
                "Aguarde",
                "O sistema ainda está inicializando a conexão com o banco."
            )
            return

        from app.controllers.cad_produtos_controller import ProdutosController
        self._abrir_subjanela(ProdutosController, "Cadastro de Produtos")

    def abrir_motivos_entrada(self):
        if not self._database_ready:
            QMessageBox.information(
                self,
                "Aguarde",
                "O sistema ainda está inicializando a conexão com o banco."
            )
            return

        from app.controllers.cad_motivo_entrada_controller import MotivoEntradaController
        self._abrir_subjanela(MotivoEntradaController,
                              "Cadastro de Motivos de Entrada")
