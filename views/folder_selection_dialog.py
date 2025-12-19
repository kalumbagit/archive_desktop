

# views/folder_selection_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTreeWidget, QTreeWidgetItem)
from PySide6.QtCore import Qt
from controllers.folder_controller import FolderController
from database.db_manager import DatabaseManager

class FolderSelectionDialog(QDialog):
    """Dialog for selecting a folder from archive"""
    
    def __init__(self, parent, user,db:DatabaseManager):
        super().__init__(parent)
        self.user = user
        self.db=db
        self.folder_controller = FolderController(self.user,self.db)
        self.selected_folder = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Sélectionner un dossier")
        self.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Sélectionnez un dossier de destination:")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Folder tree
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabel("Dossiers")
        self.folder_tree.itemClicked.connect(self.on_folder_selected)
        layout.addWidget(self.folder_tree)
        
        # Load folders
        self.load_folders()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.select_btn = QPushButton("Sélectionner")
        self.select_btn.setEnabled(False)
        self.select_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.select_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_folders(self):
        """Load folder tree"""
        self.folder_tree.clear()
        folders = self.folder_controller.get_root_folders()
        
        for folder in folders:
            self.add_folder_to_tree(folder, None)
    
    def add_folder_to_tree(self, folder, parent_item):
        """Recursively add folders to tree"""
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
        """Handle folder selection"""
        self.selected_folder = item.data(0, Qt.UserRole)
        self.select_btn.setEnabled(True)

