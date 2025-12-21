"""
views/main_window.py - Fenêtre principale avec gestion de la déconnexion
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTreeWidget, QTreeWidgetItem, QPushButton, QLabel,
                               QLineEdit, QToolBar, QMenu, QMessageBox, QFileDialog,
                               QSplitter, QListWidget, QComboBox, QApplication)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QCloseEvent
from controllers.folder_controller import FolderController
from controllers.file_controller import FileController
from controllers.audit_controller import AuditController
from database.db_manager import DatabaseManager

class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self, user, db: DatabaseManager):
        super().__init__()
        self.user = user
        self.db = db
        self.current_folder = None
        self.should_logout = False  # Flag pour gérer la déconnexion
        
        # Controllers
        self.folder_controller = FolderController(user, self.db)
        self.file_controller = FileController(user, self.db)
        self.audit_controller = AuditController(user, self.db)
        
        self.init_ui()
        self.load_folders()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        self.setWindowTitle(f"Gestionnaire d'Archives - {self.user.username}")
        self.setGeometry(100, 100, 1200, 700)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Top bar with search and filters
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Splitter for folder tree and file list
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Folder tree
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabel("Dossiers")
        self.folder_tree.itemClicked.connect(self.on_folder_selected)
        self.folder_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.folder_tree.customContextMenuRequested.connect(self.show_folder_context_menu)
        splitter.addWidget(self.folder_tree)
        
        # Right panel - File list
        file_panel = QWidget()
        file_layout = QVBoxLayout(file_panel)
        
        file_header = QLabel("Fichiers")
        file_header.setStyleSheet("font-size: 14px; font-weight: bold;")
        file_layout.addWidget(file_header)
        
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_file_context_menu)
        file_layout.addWidget(self.file_list)
        
        splitter.addWidget(file_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage('Prêt')
    
    def create_toolbar(self):
        """Créer la barre d'outils"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # New folder action
        new_folder_action = QAction("Nouveau Dossier", self)
        new_folder_action.triggered.connect(self.create_new_folder)
        toolbar.addAction(new_folder_action)
        
        # Import action
        import_action = QAction("Importer", self)
        import_action.triggered.connect(self.open_import_window)
        toolbar.addAction(import_action)
        
        # Search action
        search_action = QAction("Rechercher", self)
        search_action.triggered.connect(self.open_search_window)
        toolbar.addAction(search_action)
        
        toolbar.addSeparator()
        
        # Settings action
        settings_action = QAction("Paramètres", self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
    
    def create_menu_bar(self):
        """Créer la barre de menu"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("Fichier")
        
        import_action = QAction("Importer des fichiers", self)
        import_action.triggered.connect(self.import_files)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        logout_action = QAction("Déconnexion", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("Quitter", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("Affichage")
        
        refresh_action = QAction("Actualiser", self)
        refresh_action.triggered.connect(self.refresh_view)
        view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("Aide")
        
        about_action = QAction("À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_top_bar(self):
        """Créer la barre supérieure avec recherche et tri"""
        top_bar = QWidget()
        layout = QHBoxLayout(top_bar)
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.returnPressed.connect(self.quick_search)
        layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍")
        search_btn.clicked.connect(self.quick_search)
        layout.addWidget(search_btn)
        
        # Sort by combo
        layout.addWidget(QLabel("Trier par:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Nom", "Date", "Année", "Thème", "Secteur"])
        self.sort_combo.currentTextChanged.connect(self.sort_folders)
        layout.addWidget(self.sort_combo)
        
        layout.addStretch()
        
        return top_bar
    
    def load_folders(self):
        """Charger les dossiers racine"""
        self.folder_tree.clear()
        folders = self.folder_controller.get_root_folders()
        
        for folder in folders:
            self.add_folder_to_tree(folder, None)
    
    def add_folder_to_tree(self, folder, parent_item):
        """Ajouter un dossier à l'arborescence de manière récursive"""
        if parent_item is None:
            item = QTreeWidgetItem(self.folder_tree)
        else:
            item = QTreeWidgetItem(parent_item)
        
        item.setText(0, folder.name)
        item.setData(0, Qt.UserRole, folder)
        
        # Load subfolders
        for subfolder in folder.subfolders:
            self.add_folder_to_tree(subfolder, item)
    
    def on_folder_selected(self, item):
        """Gérer la sélection d'un dossier"""
        folder = item.data(0, Qt.UserRole)
        self.current_folder = folder
        self.load_files(folder)
    
    def load_files(self, folder):
        """Charger les fichiers d'un dossier"""
        self.file_list.clear()
        files = self.file_controller.get_files_in_folder(folder.id)
        
        for file in files:
            self.file_list.addItem(f"{file.name} ({self.format_size(file.file_size)})")
            item = self.file_list.item(self.file_list.count() - 1)
            item.setData(Qt.UserRole, file)
    
    def format_size(self, size):
        """Formatter la taille du fichier"""
        if size is None:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def on_file_double_clicked(self, item):
        """Ouvrir la prévisualisation du fichier"""
        file = item.data(Qt.UserRole)
        self.audit_controller.log_action('VIEW', 'FILE', file.id)
        
        # Import dynamique pour éviter la circularité
        from views.preview_window import PreviewWindow
        preview = PreviewWindow(file, self)
        preview.exec()
    
    def create_new_folder(self):
        """Créer un nouveau dossier"""
        from views.folder_dialog import FolderDialog
        dialog = FolderDialog(self, self.db, parent_folder=self.current_folder)
        if dialog.exec():
            self.load_folders()
    
    def import_files(self):
        """Importer des fichiers"""
        if self.current_folder is None:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un dossier d'abord")
            return
        
        files, _ = QFileDialog.getOpenFileNames(self, "Sélectionner des fichiers")
        if files:
            for file_path in files:
                self.file_controller.add_file(file_path, self.current_folder.id)
            self.load_files(self.current_folder)
            QMessageBox.information(self, "Succès", f"{len(files)} fichier(s) importé(s)")
    
    def open_import_window(self):
        """Ouvrir la fenêtre d'import"""
        from views.import_window import ImportWindow
        window = ImportWindow(self, self.db)
        if window.exec():
            self.refresh_view()
    
    def open_search_window(self):
        """Ouvrir la fenêtre de recherche"""
        from views.search_window import SearchWindow
        window = SearchWindow(self, self.db)
        window.show()
    
    def open_settings(self):
        """Ouvrir les paramètres"""
        from views.settings_window import SettingsWindow
        window = SettingsWindow(self)
        window.exec()
    
    def quick_search(self):
        """Recherche rapide"""
        query = self.search_input.text()
        if query:
            self.statusBar().showMessage(f"Recherche: {query}")
    
    def sort_folders(self, criteria):
        """Trier les dossiers"""
        self.statusBar().showMessage(f"Tri par: {criteria}")
    
    def show_folder_context_menu(self, position):
        """Afficher le menu contextuel des dossiers"""
        menu = QMenu()
        
        rename_action = menu.addAction("Renommer")
        delete_action = menu.addAction("Supprimer")
        properties_action = menu.addAction("Propriétés")
        
        action = menu.exec_(self.folder_tree.mapToGlobal(position))
        
        if action == delete_action:
            self.delete_folder()
    
    def show_file_context_menu(self, position):
        """Afficher le menu contextuel des fichiers"""
        menu = QMenu()
        
        open_action = menu.addAction("Ouvrir")
        download_action = menu.addAction("Télécharger")
        delete_action = menu.addAction("Supprimer")
        
        action = menu.exec_(self.file_list.mapToGlobal(position))
    
    def delete_folder(self):
        """Supprimer un dossier"""
        reply = QMessageBox.question(
            self, 
            'Confirmation', 
            'Êtes-vous sûr de vouloir supprimer ce dossier?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Implémenter la suppression
            pass
    
    def refresh_view(self):
        """Actualiser la vue"""
        self.load_folders()
        if self.current_folder:
            self.load_files(self.current_folder)
        self.statusBar().showMessage('Actualisé')
    
    def logout(self):
        """Déconnexion et retour à l'écran de login"""
        reply = QMessageBox.question(
            self,
            'Déconnexion',
            'Êtes-vous sûr de vouloir vous déconnecter?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Logger l'action de déconnexion
            self.audit_controller.log_action('LOGOUT', 'USER', self.user.id)
            
            # Définir le flag de déconnexion
            self.should_logout = True
            
            # Fermer la fenêtre principale
            self.close()
            
            # Quitter la boucle d'événements pour revenir au login
            QApplication.quit()
    
    def closeEvent(self, event: QCloseEvent):
        """Gérer la fermeture de la fenêtre"""
        if not self.should_logout:
            # L'utilisateur ferme l'application normalement (croix rouge)
            reply = QMessageBox.question(
                self,
                'Quitter',
                'Êtes-vous sûr de vouloir quitter l\'application?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Logger la fermeture
                self.audit_controller.log_action('LOGOUT', 'USER', self.user.id)
                event.accept()
            else:
                event.ignore()
        else:
            # Déconnexion demandée, accepter la fermeture
            event.accept()
    
    def show_about(self):
        """Afficher À propos"""
        QMessageBox.about(
            self, 
            "À propos", 
            "Gestionnaire d'Archives Numériques\nVersion 1.0\n\n"
            "Application de gestion d'archives avec PySide6"
        )