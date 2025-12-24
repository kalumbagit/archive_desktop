from pathlib import Path
import sys

def load_resource(relative_path: str, mode: str = "text", encoding: str = "utf-8"):
    """
    Charger un fichier de ressource (QSS, JSON, config, etc.)
    Fonctionne en mode développement et avec PyInstaller (sys._MEIPASS).

    :param relative_path: chemin relatif du fichier (ex: "ressources/styles/dark_theme.qss")
    :param mode: "text" (par défaut) ou "binary"
    :param encoding: encodage utilisé si mode="text"
    :return: contenu du fichier (str ou bytes)
    """
    # Déterminer la base selon si on est en exécutable ou en dev
    if getattr(sys, 'frozen', False):  # si packagé avec PyInstaller
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent

    file_path = base_path / relative_path

    if not file_path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {file_path}")

    if mode == "binary":
        with open(file_path, "rb") as f:
            return f.read()
    else:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
