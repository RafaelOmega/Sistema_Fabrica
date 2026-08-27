import sys
from PySide6.QtWidgets import QApplication
from app.utils.logger import setup_logging
from app.utils.theme import aplicar_tema
from app.database.connection import init_db
from app.controllers.main_window_controller import MainWindowController


def main():
    logger = setup_logging()
    logger.info("Iniciando aplicação")

    try:
        init_db()
        logger.info("Banco de dados inicializado")
    except Exception as e:
        logger.critical(f"Erro ao conectar no banco: {e}")
        sys.exit(1)

    app = QApplication(sys.argv)
    aplicar_tema(app)
    logger.info("Tema aplicado")

    window = MainWindowController()
    window.showMaximized()
    logger.info("Janela principal aberta")

    exit_code = app.exec()
    logger.info(f"Aplicação encerrada (código {exit_code})")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
