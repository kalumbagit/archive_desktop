# views/folder_view_window.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QGroupBox, QScrollArea, QWidget,
                               QMessageBox, QMenu, QTreeWidget, QTreeWidgetItem,
                               QSplitter)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from controllers.file_controller import FileController
from controllers.folder_controller import FolderController
from controllers.audit_controller import AuditController
from database.db_manager import DatabaseManager

class FolderViewWindow(QDialog):
    """Fenêtre de visualisation détaillée d'un dossier"""
    
    def __init__(self, folder, user, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.folder = folder
        self.user = user
        self.db = db
        self.file_controller = FileController(user, db)
        self.folder_controller = FolderController(user, db)
        self.audit_controller = AuditController(user, db)
        
        # Logger la consultation
        self.audit_controller.log_action('VIEW', 'FOLDER', folder.id)
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        self.setWindowTitle(f"Dossier: {self.folder.name}")
        self.setGeometry(150, 150, 1000, 700)
        
        main_layout = QVBoxLayout()
        
        # Header section avec informations du dossier
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Splitter pour sous-dossiers et fichiers
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel gauche: Sous-dossiers
        subfolders_panel = self.create_subfolders_panel()
        splitter.addWidget(subfolders_panel)
        
        # Panel droit: Fichiers
        files_panel = self.create_files_panel()
        splitter.addWidget(files_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def create_header(self):
        """Créer l'en-tête avec les informations du dossier"""
        header_group = QGroupBox("Informations du dossier")
        header_layout = QVBoxLayout()
        
        # Nom du dossier
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("<b>Nom:</b>"))
        name_label = QLabel(self.folder.name)
        name_label.setStyleSheet("font-size: 16px; color: #2c3e50;")
        name_layout.addWidget(name_label)
        name_layout.addStretch()
        header_layout.addLayout(name_layout)
        
        # Deuxième ligne: Année, Thème, Secteur
        info_layout = QHBoxLayout()
        
        if self.folder.year:
            info_layout.addWidget(QLabel("<b>Année:</b>"))
            info_layout.addWidget(QLabel(str(self.folder.year)))
            info_layout.addWidget(QLabel(" | "))
        
        if self.folder.theme:
            info_layout.addWidget(QLabel("<b>Thème:</b>"))
            info_layout.addWidget(QLabel(self.folder.theme))
            info_layout.addWidget(QLabel(" | "))
        
        if self.folder.sector:
            info_layout.addWidget(QLabel("<b>Secteur:</b>"))
            info_layout.addWidget(QLabel(self.folder.sector))
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        # Description
        if self.folder.description:
            header_layout.addWidget(QLabel("<b>Description:</b>"))
            desc_label = QLabel(self.folder.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
            header_layout.addWidget(desc_label)
        
        header_group.setLayout(header_layout)
        return header_group
    
    def create_subfolders_panel(self):
        """Créer le panel des sous-dossiers"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Titre
        title = QLabel("Sous-dossiers")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Tree widget pour les sous-dossiers
        self.subfolders_tree = QTreeWidget()
        self.subfolders_tree.setHeaderLabel("Nom")
        self.subfolders_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.subfolders_tree.customContextMenuRequested.connect(self.show_subfolder_context_menu)
        self.subfolders_tree.itemDoubleClicked.connect(self.open_subfolder)
        layout.addWidget(self.subfolders_tree)
        
        # Compteur
        self.subfolder_count_label = QLabel("0 sous-dossier(s)")
        self.subfolder_count_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(self.subfolder_count_label)
        
        return panel
    
    def create_files_panel(self):
        """Créer le panel des fichiers"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Titre
        title = QLabel("Fichiers")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Table pour les fichiers
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(4)
        self.files_table.setHorizontalHeaderLabels([
            "Nom", "Type", "Taille", "Date d'ajout"
        ])
        self.files_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.files_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.files_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.files_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.files_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.files_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.files_table.customContextMenuRequested.connect(self.show_file_context_menu)
        self.files_table.doubleClicked.connect(self.open_file)
        layout.addWidget(self.files_table)
        
        # Compteur
        self.file_count_label = QLabel("0 fichier(s)")
        self.file_count_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(self.file_count_label)
        
        return panel
    
    def load_data(self):
        """Charger les sous-dossiers et fichiers"""
        self.load_subfolders()
        self.load_files()
    
    def load_subfolders(self):
        """Charger les sous-dossiers"""
        self.subfolders_tree.clear()
        
        # Récupérer les sous-dossiers
        subfolders = self.folder_controller.get_subfolders(self.folder.id)
        
        for subfolder in subfolders:
            self.add_subfolder_to_tree(subfolder, None)
        
        self.subfolder_count_label.setText(f"{len(subfolders)} sous-dossier(s)")
    
    def add_subfolder_to_tree(self, folder, parent_item):
        """Ajouter un sous-dossier à l'arbre de manière récursive"""
        if parent_item is None:
            item = QTreeWidgetItem(self.subfolders_tree)
        else:
            item = QTreeWidgetItem(parent_item)
        
        # Nom avec icône de dossier
        item.setText(0, f"📁 {folder.name}")
        item.setData(0, Qt.UserRole, folder)
        
        # Charger les sous-dossiers récursivement
        for subfolder in folder.subfolders:
            self.add_subfolder_to_tree(subfolder, item)
    
    def load_files(self):
        """Charger les fichiers du dossier"""
        self.files_table.setRowCount(0)
        
        # Récupérer les fichiers
        files = self.file_controller.get_files_in_folder(self.folder.id)
        
        for file in files:
            row = self.files_table.rowCount()
            self.files_table.insertRow(row)
            
            # Nom
            name_item = QTableWidgetItem(file.name)
            name_item.setData(Qt.UserRole, file)
            self.files_table.setItem(row, 0, name_item)
            
            # Type
            file_type = self.get_file_type(file.name)
            self.files_table.setItem(row, 1, QTableWidgetItem(file_type))
            
            # Taille
            size = self.format_size(file.file_size)
            self.files_table.setItem(row, 2, QTableWidgetItem(size))
            
            # Date
            date = file.created_at.strftime("%d/%m/%Y %H:%M") if file.created_at else "N/A"
            self.files_table.setItem(row, 3, QTableWidgetItem(date))
        
        self.file_count_label.setText(f"{len(files)} fichier(s)")
    
    def get_file_type(self, filename):
        """Obtenir le type de fichier à partir de l'extension"""
        if '.' not in filename:
            return "Fichier"
        
        ext = filename.rsplit('.', 1)[1].lower()
        type_map = {
            'pdf': 'PDF',
            'doc': 'Word', 'docx': 'Word',
            'xls': 'Excel', 'xlsx': 'Excel',
            'ppt': 'PowerPoint', 'pptx': 'PowerPoint',
            'txt': 'Texte',
            'jpg': 'Image', 'jpeg': 'Image', 'png': 'Image', 'gif': 'Image',
            'zip': 'Archive', 'rar': 'Archive', '7z': 'Archive'
        }
        return type_map.get(ext, ext.upper())
    
    def format_size(self, size):
        """Formater la taille du fichier"""
        if size is None:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def open_subfolder(self, item):
        """Ouvrir un sous-dossier"""
        subfolder = item.data(0, Qt.UserRole)
        if subfolder:
            # Ouvrir une nouvelle fenêtre pour le sous-dossier
            subfolder_window = FolderViewWindow(subfolder, self.user, self.db, self)
            subfolder_window.exec()
    
    def open_file(self, index):
        """Ouvrir un fichier"""
        row = index.row()
        item = self.files_table.item(row, 0)
        file = item.data(Qt.UserRole)
        
        if file:
            # Logger la consultation
            self.audit_controller.log_action('VIEW', 'FILE', file.id)
            
            # Ouvrir la prévisualisation
            from views.preview_window import PreviewWindow
            preview = PreviewWindow(file, self)
            preview.exec()
    
    def show_subfolder_context_menu(self, position):
        """Afficher le menu contextuel pour les sous-dossiers"""
        item = self.subfolders_tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        
        open_action = menu.addAction("📂 Ouvrir")
        menu.addSeparator()
        properties_action = menu.addAction("ℹ️ Propriétés")
        
        action = menu.exec_(self.subfolders_tree.mapToGlobal(position))
        
        if action == open_action:
            self.open_subfolder(item)
        elif action == properties_action:
            subfolder = item.data(0, Qt.UserRole)
            self.show_folder_properties(subfolder)
    
    def show_file_context_menu(self, position):
        """Afficher le menu contextuel pour les fichiers"""
        item = self.files_table.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        
        open_action = menu.addAction("👁️ Ouvrir")
        download_action = menu.addAction("💾 Télécharger")
        menu.addSeparator()
        properties_action = menu.addAction("ℹ️ Propriétés")
        
        action = menu.exec_(self.files_table.mapToGlobal(position))
        
        if action == open_action:
            self.open_file(self.files_table.indexAt(position))
        elif action == download_action:
            row = self.files_table.row(item)
            file_item = self.files_table.item(row, 0)
            file = file_item.data(Qt.UserRole)
            self.download_file(file)
        elif action == properties_action:
            row = self.files_table.row(item)
            file_item = self.files_table.item(row, 0)
            file = file_item.data(Qt.UserRole)
            self.show_file_properties(file)
    
    def download_file(self, file):
        """Télécharger un fichier"""
        from PySide6.QtWidgets import QFileDialog
        import shutil
        
        # Demander où sauvegarder
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer sous",
            file.name,
            "Tous les fichiers (*.*)"
        )
        
        if save_path:
            try:
                # Copier le fichier
                shutil.copy2(file.file_path, save_path)
                
                # Logger l'action
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
<b>Type:</b> {self.get_file_type(file.name)}<br>
<b>Taille:</b> {self.format_size(file.file_size)}<br>
<b>Chemin:</b> {file.file_path}<br>
<b>Ajouté le:</b> {file.created_at.strftime('%d/%m/%Y %H:%M') if file.created_at else 'N/A'}<br>
<b>Ajouté par:</b> {file.created_by}
        """
        
        QMessageBox.information(self, f"Propriétés: {file.name}", info)