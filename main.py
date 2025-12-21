"""
main.py - Point d'entrée de l'application avec gestion de la déconnexion
"""
import sys
from PySide6.QtWidgets import QApplication
from database.db_manager import DatabaseManager
from config.settings import Settings
from views.login_window import LoginWindow
from views.main_window import MainWindow
from utils.theme_manager import ThemeManager

def main():
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Gestionnaire d'Archives Numériques")
    app.setOrganizationName("ArchiveManager")
    
    # Initialize database
    db = DatabaseManager()
    settings = Settings()
    
    db_config = settings.get('database')
    db.initialize(
        db_type=db_config.get('type', 'sqlite'),
        db_path=db_config.get('path')
    )

    # Appliquer le thème choisi
    theme = settings.get('ui.theme', 'light')
    if theme == 'system':
        # Détection simple du thème système
        palette = app.palette()
        bg_color = palette.window().color().lightness()
        theme = 'dark' if bg_color < 128 else 'light'
    ThemeManager.apply_theme(theme)
    
    # Boucle principale de l'application avec gestion de la reconnexion
    while True:
        # Show login window
        login_window = LoginWindow(db)
        
        if login_window.exec():
            # User logged in successfully
            user = login_window.user
            
            # Show main window
            main_window = MainWindow(user, db)
            main_window.show()
            
            # Attendre la fermeture de la fenêtre principale
            app.exec()
            
            # Vérifier si l'utilisateur veut se reconnecter
            if not main_window.should_logout:
                # L'utilisateur a fermé l'application normalement
                break
            # Sinon, on continue la boucle pour réafficher le login
        else:
            # User cancelled login
            break
    
    sys.exit(0)

if __name__ == "__main__":
    main()