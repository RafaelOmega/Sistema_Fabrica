from app.utils.theme import aplicar_tema
from app.utils.logger import setup_logging, get_logger
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QObject, QThread, QTimer, Signal, Slot
from time import perf_counter
import traceback
import sys

sys.dont_write_bytecode = True


class DatabaseInitWorker(QObject):
    finished = Signal(float)
    failed = Signal(str, str)

    @Slot()
    def run(self):
        try:
            inicio = perf_counter()

            from app.database.connection import init_db
            init_db()

            self.finished.emit(perf_counter() - inicio)
        except Exception as e:
            self.failed.emit(str(e), traceback.format_exc())


class DatabaseCallbackHandler(QObject):
    def __init__(self, splash, window, parent=None):
        super().__init__(parent)
        self._splash = splash
        self._window = window
        self._logger = get_logger("main")

    @Slot(float)
    def on_ready(self, elapsed):
        self._logger.info(f"Banco de dados inicializado em {elapsed:.3f}s")
        self._splash.fechar()
        self._window.showMaximized()
        if hasattr(self._window, "on_database_ready"):
            self._window.on_database_ready()

    @Slot(str, str)
    def on_failed(self, error_message, error_trace):
        self._logger.critical(f"Erro ao conectar no banco: {error_message}")
        self._logger.critical(error_trace)
        self._splash.fechar()

        if hasattr(self._window, "on_database_failed"):
            self._window.on_database_failed(error_message)

        QMessageBox.critical(
            None,
            "Erro de conexão",
            f"Erro ao conectar no banco:\n{error_message}"
        )
        QApplication.quit()


def main():
    inicio_total = perf_counter()

    logger = setup_logging()
    logger.info("Iniciando aplicação")

    app = QApplication(sys.argv)

    aplicar_tema(app)
    logger.info("Tema aplicado")

    from app.controllers.carregamento_controller import CarregamentoController
    from app.controllers.main_window_controller import MainWindowController

    splash = CarregamentoController()
    splash.mostrar()
    app.processEvents()
    logger.info("Splash de carregamento exibido")

    window = MainWindowController()
    logger.info(
        f"Janela principal criada em {perf_counter() - inicio_total:.3f}s"
    )

    handler = DatabaseCallbackHandler(splash, window, parent=app)

    db_thread = QThread()
    db_worker = DatabaseInitWorker()

    db_worker.moveToThread(db_thread)

    db_thread.started.connect(db_worker.run)
    db_worker.finished.connect(db_thread.quit)
    db_worker.finished.connect(db_worker.deleteLater)
    db_worker.failed.connect(db_thread.quit)
    db_worker.failed.connect(db_worker.deleteLater)
    db_thread.finished.connect(db_thread.deleteLater)

    db_worker.finished.connect(handler.on_ready)
    db_worker.failed.connect(handler.on_failed)

    app._db_thread = db_thread
    app._db_worker = db_worker
    app._splash = splash
    app._handler = handler

    QTimer.singleShot(100, db_thread.start)

    exit_code = app.exec()
    logger.info(f"Aplicação encerrada (código {exit_code})")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
