# views/folder_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QSpinBox, QTextEdit,
                               QFormLayout, QMessageBox)
from PySide6.QtCore import Qt
from controllers.folder_controller import FolderController
from utils.validators import Validator
from database.db_manager import DatabaseManager

class FolderDialog(QDialog):
    """Dialog for creating or editing folders"""
    
    def __init__(self, parent, db: DatabaseManager, parent_folder=None, folder_to_edit=None):
        super().__init__(parent)
        self.user = parent.user
        self.parent_folder = parent_folder
        self.folder_to_edit = folder_to_edit
        self.folder_controller = FolderController(self.user, db)
        
        self.setWindowTitle("Nouveau dossier" if not folder_to_edit else "Modifier le dossier")
        self.init_ui()
        
        if folder_to_edit:
            self.load_folder_data()
    
    def init_ui(self):
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Folder name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom du dossier")
        form_layout.addRow("Nom *:", self.name_input)
        
        # Year
        self.year_input = QSpinBox()
        self.year_input.setRange(1900, 2100)
        self.year_input.setValue(2024)
        self.year_input.setSpecialValueText("Non spécifié")
        self.year_input.setValue(0)
        form_layout.addRow("Année:", self.year_input)
        
        # Theme
        self.theme_input = QLineEdit()
        self.theme_input.setPlaceholderText("Ex: Finances, RH, Juridique...")
        form_layout.addRow("Thème:", self.theme_input)
        
        # Sector
        self.sector_input = QLineEdit()
        self.sector_input.setPlaceholderText("Ex: Commercial, Technique...")
        form_layout.addRow("Secteur:", self.sector_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description du dossier (optionnel)")
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_input)
        
        # Parent folder info
        if self.parent_folder:
            parent_label = QLabel(f"📁 Sous-dossier de: {self.parent_folder.name}")
            parent_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
            form_layout.addRow("", parent_label)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_btn.clicked.connect(self.save_folder)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_folder_data(self):
        """Load existing folder data for editing"""
        folder = self.folder_to_edit
        self.name_input.setText(folder.name)
        
        if folder.year:
            self.year_input.setValue(folder.year)
        
        if folder.theme:
            self.theme_input.setText(folder.theme)
        
        if folder.sector:
            self.sector_input.setText(folder.sector)
        
        if folder.description:
            self.description_input.setPlainText(folder.description)
    
    def save_folder(self):
        """Save or update folder"""
        name = self.name_input.text().strip()
        year = self.year_input.value() if self.year_input.value() > 0 else None
        theme = self.theme_input.text().strip() or None
        sector = self.sector_input.text().strip() or None
        description = self.description_input.toPlainText().strip() or None
        
        # Validate
        valid, msg = Validator.validate_folder_name(name)
        if not valid:
            QMessageBox.warning(self, "Validation", msg)
            return
        
        if year:
            valid, msg = Validator.validate_year(year)
            if not valid:
                QMessageBox.warning(self, "Validation", msg)
                return
        
        # Save
        if self.folder_to_edit:
            # Update existing folder
            success, result = self.folder_controller.update_folder(
                self.folder_to_edit.id,
                name=name,
                year=year,
                theme=theme,
                sector=sector,
                description=description
            )
        else:
            # Create new folder
            parent_id = self.parent_folder.id if self.parent_folder else None
            success, result = self.folder_controller.create_folder(
                name=name,
                year=year,
                theme=theme,
                sector=sector,
                description=description,
                parent_id=parent_id
            )
        
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", result)
