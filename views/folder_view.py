# =============================================================================
# FICHIER 3: views/folder_view.py - COMPLET (NOUVEAU)
# =============================================================================
"""
views/folder_view.py
Vue détaillée d'un dossier avec ses fichiers et sous-dossiers
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QListWidget, QTreeWidget, QTreeWidgetItem,
                               QSplitter, QMessageBox, QMenu)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

class FolderView(QWidget):
    """Vue détaillée d'un dossier"""
    
    # Signaux
    folder_selected = Signal(object)  # Émis quand un sous-dossier est sélectionné
    file_selected = Signal(object)    # Émis quand un fichier est sélectionné
    file_double_clicked = Signal(object)  # Émis lors d'un double-clic sur un fichier
    
    def __init__(self, folder, file_controller, parent=None):
        """
        Initialiser la vue du dossier
        
        Args:
            folder: Objet Folder à afficher
            file_controller: Contrôleur de fichiers
            parent: Widget parent
        """
        super().__init__(parent)
        self.folder = folder
        self.file_controller = file_controller
        self.init_ui()
        self.load_content()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        layout = QVBoxLayout()
        
        # En-tête du dossier
        header = self.create_header()
        layout.addWidget(header)
        
        # Splitter pour sous-dossiers et fichiers
        splitter = QSplitter(Qt.Horizontal)
        
        # Liste des sous-dossiers
        subfolder_widget = QWidget()
        subfolder_layout = QVBoxLayout(subfolder_widget)
        subfolder_layout.addWidget(QLabel("Sous-dossiers:"))
        
        self.subfolder_tree = QTreeWidget()
        self.subfolder_tree.setHeaderLabel("Nom")
        self.subfolder_tree.itemDoubleClicked.connect(self.on_subfolder_double_clicked)
        subfolder_layout.addWidget(self.subfolder_tree)
        
        splitter.addWidget(subfolder_widget)
        
        # Liste des fichiers
        file_widget = QWidget()
        file_layout = QVBoxLayout(file_widget)
        file_layout.addWidget(QLabel("Fichiers:"))
        
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.on_file_clicked)
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_file_context_menu)
        file_layout.addWidget(self.file_list)
        
        splitter.addWidget(file_widget)
        
        layout.addWidget(splitter)
        
        self.setLayout(layout)
    
    def create_header(self):
        """Créer l'en-tête du dossier"""
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Nom du dossier
        name_label = QLabel(f"📁 {self.folder.name}")
        name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(name_label)
        
        # Métadonnées
        meta_text = []
        if self.folder.year:
            meta_text.append(f"Année: {self.folder.year}")
        if self.folder.theme:
            meta_text.append(f"Thème: {self.folder.theme}")
        if self.folder.sector:
            meta_text.append(f"Secteur: {self.folder.sector}")
        
        if meta_text:
            meta_label = QLabel(" | ".join(meta_text))
            meta_label.setStyleSheet("font-size: 12px;")
            layout.addWidget(meta_label)
        
        # Description
        if self.folder.description:
            desc_label = QLabel(self.folder.description)
            desc_label.setStyleSheet("font-size: 11px; font-style: italic;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        header.setLayout(layout)
        return header
    
    def load_content(self):
        """Charger le contenu du dossier"""
        # Charger les sous-dossiers
        self.subfolder_tree.clear()
        for subfolder in self.folder.subfolders:
            item = QTreeWidgetItem(self.subfolder_tree)
            item.setText(0, subfolder.name)
            item.setData(0, Qt.UserRole, subfolder)
        
        # Charger les fichiers
        self.file_list.clear()
        files = self.file_controller.get_files_in_folder(self.folder.id)
        
        for file in files:
            self.file_list.addItem(f"{file.name} ({self.format_size(file.file_size)})")
            item = self.file_list.item(self.file_list.count() - 1)
            item.setData(Qt.UserRole, file)
    
    def format_size(self, size):
        """Formater la taille du fichier"""
        if size is None:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def on_subfolder_double_clicked(self, item):
        """Gérer le double-clic sur un sous-dossier"""
        subfolder = item.data(0, Qt.UserRole)
        self.folder_selected.emit(subfolder)
    
    def on_file_clicked(self, item):
        """Gérer le clic sur un fichier"""
        file = item.data(Qt.UserRole)
        self.file_selected.emit(file)
    
    def on_file_double_clicked(self, item):
        """Gérer le double-clic sur un fichier"""
        file = item.data(Qt.UserRole)
        self.file_double_clicked.emit(file)
    
    def show_file_context_menu(self, position):
        """Afficher le menu contextuel des fichiers"""
        item = self.file_list.itemAt(position)
        if not item:
            return
        
        file = item.data(Qt.UserRole)

