from PySide6.QtCore import Qt, QTimer, QDateTime
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

        self._janelas_abertas = {}

        self._conectar_sinais()
        self._iniciar_statusbar()

        logger.info("MainWindow inicializada")

    def _conectar_sinais(self):
        self.ui.actionProdutos.triggered.connect(self.abrir_produtos)
        self.ui.actionMotivo_Entrada.triggered.connect(
            self.abrir_motivo_entrada)
        self.ui.actionEntrada.triggered.connect(self.abrir_entrada)
        self.ui.actionFicha_Tecnica.triggered.connect(self.abrir_ficha_tecnica)
        self.ui.actionSaida.triggered.connect(self.abrir_saida)
        self.ui.actionEstoque.triggered.connect(self.abrir_estoque)
        self.ui.actionFichaKardexProduto.triggered.connect(self.abrir_kardex)

    def _iniciar_statusbar(self):
        self.ui.lb_Comandos.setText("Pronto")
        self._atualizar_statusbar()
        self._timer_statusbar = QTimer(self)
        self._timer_statusbar.timeout.connect(self._atualizar_statusbar)
        self._timer_statusbar.start(1000)

    def _atualizar_statusbar(self):
        now = QDateTime.currentDateTime()
        self.ui.dt_Data_Atual.setDate(now.date())
        self.ui.dt_Hora_Atual.setTime(now.time())

    def on_database_ready(self):
        self._habilitar_menus(True)
        self.ui.lb_Comandos.setText("Sistema pronto para uso")
        logger.info("Banco pronto - menus liberados")

    def on_database_failed(self, error_message):
        self._habilitar_menus(False)
        self.ui.lb_Comandos.setText(f"Erro: {error_message}")
        logger.error(f"Banco falhou: {error_message}")

    def _habilitar_menus(self, habilitar):
        self.ui.actionProdutos.setEnabled(habilitar)
        self.ui.actionMotivo_Entrada.setEnabled(habilitar)
        self.ui.actionEntrada.setEnabled(habilitar)
        self.ui.actionFicha_Tecnica.setEnabled(habilitar)
        self.ui.actionSaida.setEnabled(habilitar)
        self.ui.actionEstoque.setEnabled(habilitar)
        self.ui.actionFichaKardexProduto.setEnabled(habilitar)

    # --- Abertura de janelas MDI ---

    def _abrir_janela_mdi(self, chave, titulo, criar_controller, maximizar=False):
        """Abre uma janela no MDI. Se já estiver aberta e válida, traz para frente."""
        if chave in self._janelas_abertas:
            subwindow = self._janelas_abertas[chave]
            if subwindow is not None:
                widget = subwindow.widget()
                if widget is not None and not widget.isHidden():
                    self.ui.mdiArea.setActiveSubWindow(subwindow)
                    subwindow.showNormal()
                    subwindow.setFocus()
                    logger.debug(
                        f"Janela '{titulo}' já aberta - trazendo para frente")
                    return
            self._janelas_abertas.pop(chave, None)

        try:
            controller = criar_controller()
            subwindow = QMdiSubWindow()
            subwindow.setWindowTitle(titulo)
            subwindow.setWidget(controller)
            self.ui.mdiArea.addSubWindow(subwindow)

            if maximizar:
                subwindow.showMaximized()
            else:
                subwindow.resize(controller.size())
                subwindow.show()

            subwindow.destroyed.connect(
                lambda _, c=chave: self._janelas_abertas.pop(c, None)
            )

            self._janelas_abertas[chave] = subwindow

            logger.info(f"Janela '{titulo}' aberta no MDI")
        except Exception as e:
            logger.error(
                f"Erro ao abrir janela '{titulo}': {e}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Erro ao abrir {titulo}:\n{e}")

    def abrir_produtos(self):
        from app.controllers.cad_produtos_controller import ProdutosController
        self._abrir_janela_mdi(
            "produtos", "Cadastro de Produtos", ProdutosController,
            maximizar=False)

    def abrir_motivo_entrada(self):
        from app.controllers.cad_motivo_entrada_controller import MotivoEntradaController
        self._abrir_janela_mdi(
            "motivo_entrada", "Cadastro de Motivo de Entrada", MotivoEntradaController,
            maximizar=True)

    def abrir_ficha_tecnica(self):
        from app.controllers.ficha_tecnica_controller import FichaTecnicaController
        self._abrir_janela_mdi(
            "ficha_tecnica", "Cadastro de Ficha Técnica", FichaTecnicaController,
            maximizar=True)

    def abrir_entrada(self):
        from app.controllers.cad_entrada_controller import EntradaController
        self._abrir_janela_mdi(
            "entrada", "Entrada de Mercadorias", EntradaController,
            maximizar=True)

    def abrir_saida(self):
        from app.controllers.cad_saida_controller import SaidaController
        self._abrir_janela_mdi(
            "saida", "Saída de Mercadorias", SaidaController,
            maximizar=True)

    def abrir_estoque(self):
        from app.controllers.estoque_controller import EstoqueController
        self._abrir_janela_mdi(
            "estoque", "Estoque", EstoqueController,
            maximizar=True)

    def abrir_kardex(self):
        from app.controllers.kardex_controller import KardexController
        self._abrir_janela_mdi(
            "kardex", "Ficha Kardex do Produto", KardexController,
            maximizar=True)

    def closeEvent(self, event):
        for subwindow in list(self._janelas_abertas.values()):
            if subwindow is not None:
                subwindow.close()
        self._janelas_abertas.clear()
        super().closeEvent(event)
