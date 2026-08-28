from pathlib import Path
import sys

from app.utils.logger import get_logger

logger = get_logger("theme")


def _base_path() -> Path:
    """
    Retorna a base correta dos arquivos:
    - desenvolvimento: raiz do projeto
    - executável PyInstaller: pasta temporária do bundle
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parents[2]


def _encontrar_arquivo_tema() -> Path | None:
    """
    Procura o arquivo do tema em caminhos compatíveis com:
    - execução normal
    - execução empacotada com PyInstaller
    """
    base = _base_path()

    candidatos = [
        base / "app" / "styles" / "dark_theme.qss",
        base / "app" / "styles" / "dark_theme.txt",
        base / "styles" / "dark_theme.qss",
        base / "styles" / "dark_theme.txt",
    ]

    for caminho in candidatos:
        if caminho.exists():
            return caminho

    return None


def aplicar_tema(app) -> bool:
    """
    Aplica o tema escuro na aplicação.
    Retorna True se aplicou, False se não encontrou ou falhou.
    """
    caminho_tema = _encontrar_arquivo_tema()

    if not caminho_tema:
        logger.warning("Arquivo de tema não encontrado.")
        return False

    try:
        conteudo = caminho_tema.read_text(encoding="utf-8")
        app.setStyleSheet(conteudo)
        logger.info(f"Tema aplicado com sucesso: {caminho_tema}")
        return True
    except Exception as exc:
        logger.error(f"Erro ao aplicar tema: {exc}", exc_info=True)
        return False
