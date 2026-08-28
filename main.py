from app.utils.theme import aplicar_tema
from app.utils.logger import setup_logging
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
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


def main():
    inicio_total = perf_counter()

    logger = setup_logging()
    logger.info("Iniciando aplicação")

    app = QApplication(sys.argv)

    aplicar_tema(app)
    logger.info("Tema aplicado")

    from app.controllers.main_window_controller import MainWindowController
    window = MainWindowController()
    window.showMaximized()

    app.processEvents()

    logger.info(
        f"Janela principal exibida em {perf_counter() - inicio_total:.3f}s"
    )

    db_thread = QThread()
    db_worker = DatabaseInitWorker()

    db_worker.moveToThread(db_thread)

    db_thread.started.connect(db_worker.run)
    db_worker.finished.connect(db_thread.quit)
    db_worker.finished.connect(db_worker.deleteLater)
    db_worker.failed.connect(db_thread.quit)
    db_worker.failed.connect(db_worker.deleteLater)
    db_thread.finished.connect(db_thread.deleteLater)

    def on_database_ready(elapsed):
        logger.info(f"Banco de dados inicializado em {elapsed:.3f}s")
        if hasattr(window, "on_database_ready"):
            window.on_database_ready()

    def on_database_failed(error_message, error_trace):
        logger.critical(f"Erro ao conectar no banco: {error_message}")
        logger.critical(error_trace)

        if hasattr(window, "on_database_failed"):
            window.on_database_failed(error_message)

        QMessageBox.critical(
            window,
            "Erro de conexão",
            f"Erro ao conectar no banco:\n{error_message}"
        )
        app.quit()

    db_worker.finished.connect(on_database_ready)
    db_worker.failed.connect(on_database_failed)

    app._db_thread = db_thread
    app._db_worker = db_worker

    QTimer.singleShot(100, db_thread.start)

    exit_code = app.exec()
    logger.info(f"Aplicação encerrada (código {exit_code})")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
