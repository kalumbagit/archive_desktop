# utils/theme_manager.py
from pathlib import Path
from PySide6.QtWidgets import QApplication

class ThemeManager:
    """Manage application themes"""
    
    THEMES = {
        'light': 'resources/styles/light_theme.qss',
        'dark': 'resources/styles/dark_theme.qss'
    }
    
    @staticmethod
    def apply_theme(theme_name='light'):
        """Apply theme to application"""
        app = QApplication.instance()
        
        if theme_name not in ThemeManager.THEMES:
            theme_name = 'light'
        
        theme_path = Path(ThemeManager.THEMES[theme_name])
        
        if theme_path.exists():
            try:
                with open(theme_path, 'r', encoding='utf-8') as f:
                    stylesheet = f.read()
                    app.setStyleSheet(stylesheet)
                return True
            except Exception as e:
                print(f"Erreur lors de l'application du thème: {e}")
                return False
        else:
            # Use embedded theme
            stylesheet = ThemeManager._get_embedded_theme(theme_name)
            app.setStyleSheet(stylesheet)
            return True
    
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

