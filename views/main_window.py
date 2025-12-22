"""
views/main_window.py - Fenêtre principale avec création de fichiers
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
import os
import shutil

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
    
    def add_files_to_folder(self, folder):
        """Ajouter des fichiers à un dossier spécifique"""
        if folder is None:
            QMessageBox.warning(self, "Attention", "Aucun dossier sélectionné")
            return
        
        # Ouvrir le sélecteur de fichiers
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner des fichiers à ajouter",
            "",
            "Tous les fichiers (*.*)"
        )
        
        if not file_paths:
            return
        
        # Compteurs pour le résultat
        success_count = 0
        error_count = 0
        errors = []
        
        for file_path in file_paths:
            try:
                # Ajouter le fichier via le contrôleur
                result = self.file_controller.add_file(file_path, folder.id)
                
                if result:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"{os.path.basename(file_path)}: Échec de l'ajout")
                    
            except Exception as e:
                error_count += 1
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")
        
        # Rafraîchir la liste des fichiers si c'est le dossier actuel
        if self.current_folder and self.current_folder.id == folder.id:
            self.load_files(folder)
        
        # Afficher le résultat
        if error_count == 0:
            QMessageBox.information(
                self,
                "Succès",
                f"{success_count} fichier(s) ajouté(s) avec succès au dossier '{folder.name}'"
            )
        else:
            error_msg = f"{success_count} fichier(s) ajouté(s)\n{error_count} erreur(s):\n\n"
            error_msg += "\n".join(errors[:5])  # Afficher max 5 erreurs
            if len(errors) > 5:
                error_msg += f"\n... et {len(errors) - 5} autre(s) erreur(s)"
            
            QMessageBox.warning(self, "Résultat partiel", error_msg)
    
    def create_new_file(self, folder):
        """Créer un nouveau fichier dans un dossier"""
        if folder is None:
            QMessageBox.warning(self, "Attention", "Aucun dossier sélectionné")
            return
        
        from views.file_creation_dialog import FileCreationDialog
        
        dialog = FileCreationDialog(folder, self)
        if dialog.exec():
            # Récupérer les informations du fichier créé
            file_name = dialog.file_name
            file_type = dialog.file_type
            file_content = dialog.file_content
            
            try:
                # Créer le fichier temporaire
                from config.settings import Settings
                settings = Settings()
                storage_path = settings.get('storage.path', 'storage/files')
                
                # Créer le répertoire de stockage s'il n'existe pas
                os.makedirs(storage_path, exist_ok=True)
                
                # Chemin complet du fichier
                file_path = os.path.join(storage_path, file_name)
                
                # Écrire le contenu dans le fichier
                if file_type == 'text':
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                elif file_type == 'markdown':
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                else:  # fichier vide
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('')
                
                # Ajouter le fichier à la base de données
                result = self.file_controller.add_file(file_path, folder.id)
                
                if result:
                    # Rafraîchir la liste si c'est le dossier actuel
                    if self.current_folder and self.current_folder.id == folder.id:
                        self.load_files(folder)
                    
                    QMessageBox.information(
                        self,
                        "Succès",
                        f"Fichier '{file_name}' créé avec succès dans '{folder.name}'"
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Erreur",
                        "Échec de l'ajout du fichier à la base de données"
                    )
                    # Supprimer le fichier créé en cas d'échec
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors de la création du fichier:\n{str(e)}"
                )
    
    def import_files(self):
        """Importer des fichiers dans le dossier sélectionné"""
        if self.current_folder is None:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un dossier d'abord")
            return
        
        self.add_files_to_folder(self.current_folder)
    
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
        item = self.folder_tree.itemAt(position)
        if not item:
            return
        
        folder = item.data(0, Qt.UserRole)
        
        menu = QMenu()
        
        # Créer et ajouter des fichiers
        create_file_action = menu.addAction("📄 Créer un fichier")
        add_files_action = menu.addAction("📎 Ajouter des fichiers existants")
        menu.addSeparator()
        
        # Autres actions
        rename_action = menu.addAction("✏️ Renommer")
        delete_action = menu.addAction("🗑️ Supprimer")
        menu.addSeparator()
        properties_action = menu.addAction("ℹ️ Propriétés")
        
        action = menu.exec_(self.folder_tree.mapToGlobal(position))
        
        if action == create_file_action:
            self.create_new_file(folder)
        elif action == add_files_action:
            self.add_files_to_folder(folder)
        elif action == delete_action:
            self.delete_folder(folder)
        elif action == rename_action:
            self.rename_folder(folder, item)
        elif action == properties_action:
            self.show_folder_properties(folder)
    
    def show_file_context_menu(self, position):
        """Afficher le menu contextuel des fichiers"""
        item = self.file_list.itemAt(position)
        if not item:
            return
        
        file = item.data(Qt.UserRole)
        
        menu = QMenu()
        
        open_action = menu.addAction("👁️ Ouvrir")
        download_action = menu.addAction("💾 Télécharger")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Supprimer")
        menu.addSeparator()
        properties_action = menu.addAction("ℹ️ Propriétés")
        
        action = menu.exec_(self.file_list.mapToGlobal(position))
        
        if action == open_action:
            self.on_file_double_clicked(item)
        elif action == download_action:
            self.download_file(file)
        elif action == delete_action:
            self.delete_file(file)
        elif action == properties_action:
            self.show_file_properties(file)
    
    def download_file(self, file):
        """Télécharger/copier un fichier"""
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer sous",
            file.name,
            "Tous les fichiers (*.*)"
        )
        
        if save_path:
            try:
                shutil.copy2(file.file_path, save_path)
                self.audit_controller.log_action('DOWNLOAD', 'FILE', file.id)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Fichier téléchargé avec succès:\n{save_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors du téléchargement:\n{str(e)}"
                )
    
    def delete_file(self, file):
        """Supprimer un fichier"""
        reply = QMessageBox.question(
            self,
            'Confirmation',
            f'Êtes-vous sûr de vouloir supprimer le fichier:\n{file.name}?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.file_controller.delete_file(file.id)
            if success:
                QMessageBox.information(self, "Succès", message)
                if self.current_folder:
                    self.load_files(self.current_folder)
            else:
                QMessageBox.critical(self, "Erreur", message)
    
    def delete_folder(self, folder):
        """Supprimer un dossier"""
        reply = QMessageBox.question(
            self, 
            'Confirmation', 
            f'Êtes-vous sûr de vouloir supprimer le dossier:\n{folder.name}?\n\n'
            'Tous les sous-dossiers et fichiers seront également supprimés.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.folder_controller.delete_folder(folder.id)
            if success:
                QMessageBox.information(self, "Succès", message)
                self.load_folders()
                self.current_folder = None
                self.file_list.clear()
            else:
                QMessageBox.critical(self, "Erreur", message)
    
    def rename_folder(self, folder, item):
        """Renommer un dossier"""
        from PySide6.QtWidgets import QInputDialog
        
        new_name, ok = QInputDialog.getText(
            self,
            "Renommer le dossier",
            "Nouveau nom:",
            text=folder.name
        )
        
        if ok and new_name and new_name != folder.name:
            success, result = self.folder_controller.update_folder(
                folder.id,
                name=new_name
            )
            if success:
                QMessageBox.information(self, "Succès", "Dossier renommé avec succès")
                self.load_folders()
            else:
                QMessageBox.critical(self, "Erreur", result)
    
    def show_folder_properties(self, folder):
        """Afficher les propriétés d'un dossier"""
        info = f"""
<b>Nom:</b> {folder.name}<br>
<b>Année:</b> {folder.year or 'N/A'}<br>
<b>Thème:</b> {folder.theme or 'N/A'}<br>
<b>Secteur:</b> {folder.sector or 'N/A'}<br>
<b>Description:</b> {folder.description or 'N/A'}<br>
<b>Créé le:</b> {folder.created_at.strftime('%d/%m/%Y %H:%M') if folder.created_at else 'N/A'}
        """
        QMessageBox.information(self, f"Propriétés: {folder.name}", info)
    
    def show_file_properties(self, file):
        """Afficher les propriétés d'un fichier"""
        info = f"""
<b>Nom:</b> {file.name}<br>
<b>Taille:</b> {self.format_size(file.file_size)}<br>
<b>Chemin:</b> {file.file_path}<br>
<b>Ajouté le:</b> {file.created_at.strftime('%d/%m/%Y %H:%M') if file.created_at else 'N/A'}<br>
<b>Ajouté par:</b> {file.created_by}
        """
        QMessageBox.information(self, f"Propriétés: {file.name}", info)
    
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