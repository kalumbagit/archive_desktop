# =============================================================================
# FICHIER 1: main.py - CORRIGÉ
# =============================================================================
"""
main.py - Point d'entrée de l'application
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from database.db_manager import DatabaseManager
from config.settings import Settings
from views.login_window import LoginWindow
from views.main_window import MainWindow

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
    
    # Show login window
    login_window = LoginWindow()
    
    if login_window.exec():
        # User logged in successfully
        user = login_window.user
        
        # Show main window
        main_window = MainWindow(user)
        main_window.show()
        
        sys.exit(app.exec())
    else:
        # User cancelled login
        sys.exit(0)

if __name__ == "__main__":
    main()

