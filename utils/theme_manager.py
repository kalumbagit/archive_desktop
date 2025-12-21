# utils/theme_manager.py
from pathlib import Path
from PySide6.QtWidgets import QApplication
from ressources.styles.colors import LIGHT_COLORS, DARK_COLORS  # ✅ correction du chemin

class ThemeManager:
    """Manage application themes"""
    THEMES = {
        'light': 'resources/styles/light_theme.qss',
        'dark': 'resources/styles/dark_theme.qss'
    }
    
    @staticmethod
    def apply_theme(theme_name='light'):
        app = QApplication.instance()
        if app is None:
            print("⚠️ Aucun QApplication actif, impossible d'appliquer le thème.")
            return False

        # Vérifier que le thème demandé existe
        if theme_name not in ThemeManager.THEMES:
            print(f"⚠️ Thème '{theme_name}' inconnu, fallback vers 'light'.")
            theme_name = 'light'

        theme_path = Path(ThemeManager.THEMES[theme_name])

        # Choisir la palette
        colors = LIGHT_COLORS if theme_name == 'light' else DARK_COLORS

        stylesheet = None
        if theme_path.exists():
            try:
                stylesheet = theme_path.read_text(encoding="utf-8")
                # Remplacer les variables
                for key, value in colors.items():
                    stylesheet = stylesheet.replace(f"@{key}", value)
            except Exception as e:
                print(f"⚠️ Erreur lors de la lecture du fichier QSS: {e}")
                stylesheet = None
        else:
            print(f"⚠️ Fichier QSS introuvable: {theme_path}")

        # Fallback vers thème embarqué si problème
        if not stylesheet:
            stylesheet = ThemeManager._get_embedded_theme(theme_name)

        try:
            app.setStyleSheet(stylesheet)
            return True
        except Exception as e:
            print(f"⚠️ Impossible d'appliquer le thème: {e}")
            return False
    
    @staticmethod
    def _get_embedded_theme(theme_name):
        """Get embedded theme when file not found"""
        if theme_name == 'dark':
            return """
                QWidget {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                }
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border-radius: 5px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #14a085;
                }
            """
        else:
            return """
                QWidget {
                    background-color: #ffffff;
                    color: #2c3e50;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 5px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """
