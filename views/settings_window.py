# views/settings_window.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QCheckBox,
                               QTabWidget, QWidget, QFileDialog, QMessageBox,
                               QGroupBox, QFormLayout, QSpinBox)
from PySide6.QtCore import Qt
from config.settings import Settings

class SettingsWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.settings = Settings()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Paramètres")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        tabs.addTab(self.create_general_tab(), "Général")
        tabs.addTab(self.create_storage_tab(), "Stockage")
        tabs.addTab(self.create_database_tab(), "Base de données")
        tabs.addTab(self.create_permissions_tab(), "Droits d'accès")
        tabs.addTab(self.create_appearance_tab(), "Apparence")
        
        layout.addWidget(tabs)
        
        # Boutons action
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_storage_tab(self):
        """Create storage settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Emplacement local
        storage_group = QGroupBox("Emplacement de stockage local")
        storage_layout = QVBoxLayout()
        
        path_layout = QHBoxLayout()
        self.storage_path_input = QLineEdit()
        self.storage_path_input.setText(self.settings.get('storage.base_path'))
        path_layout.addWidget(self.storage_path_input)
        
        browse_btn = QPushButton("Parcourir")
        browse_btn.clicked.connect(self.browse_storage_path)
        path_layout.addWidget(browse_btn)
        
        storage_layout.addLayout(path_layout)
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)
        
        # Emplacement distant
        remote_group = QGroupBox("Stockage distant")
        remote_layout = QFormLayout()
        
        self.remote_storage_input = QLineEdit()
        self.remote_storage_input.setPlaceholderText("Ex: https://monserveur/archives ou chemin réseau")
        self.remote_storage_input.setText(self.settings.get('storage.remote_path', ''))
        remote_layout.addRow("URL/chemin distant:", self.remote_storage_input)
        
        remote_group.setLayout(remote_layout)
        layout.addWidget(remote_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_database_tab(self):
        """Create database settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        db_group = QGroupBox("Configuration de la base de données")
        self.db_layout = QFormLayout()
        
        # Type de base
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["SQLite", "PostgreSQL", "MySQL"])
        current_db = self.settings.get('database.type', 'sqlite')
        db_map = {'sqlite': 0, 'postgresql': 1, 'mysql': 2}
        self.db_type_combo.setCurrentIndex(db_map.get(current_db, 0))
        self.db_type_combo.currentIndexChanged.connect(self.toggle_db_fields)
        self.db_layout.addRow("Type de base:", self.db_type_combo)
        
        # Champ SQLite (chemin fichier)
        sqlite_layout = QHBoxLayout()
        self.db_path_input = QLineEdit()
        self.db_path_input.setText(self.settings.get('database.path', ''))
        sqlite_layout.addWidget(self.db_path_input)
        
        browse_db_btn = QPushButton("Parcourir")
        browse_db_btn.clicked.connect(self.browse_sqlite_path)
        sqlite_layout.addWidget(browse_db_btn)
        
        self.db_layout.addRow("Fichier SQLite:", sqlite_layout)
        
        # Champs serveur (PostgreSQL/MySQL)
        self.db_host_input = QLineEdit()
        self.db_host_input.setText(self.settings.get('database.host', 'localhost'))
        self.db_layout.addRow("Hôte:", self.db_host_input)
        
        self.db_port_input = QSpinBox() 
        self.db_port_input.setRange(1, 65535)
        self.db_port_input.setValue(int(self.settings.get('database.port', 5432)))
        self.db_layout.addRow("Port:", self.db_port_input)
        
        self.db_user_input = QLineEdit()
        self.db_user_input.setText(self.settings.get('database.user', ''))
        self.db_layout.addRow("Utilisateur:", self.db_user_input)
        
        self.db_password_input = QLineEdit()
        self.db_password_input.setEchoMode(QLineEdit.Password)
        self.db_password_input.setText(self.settings.get('database.password', ''))
        self.db_layout.addRow("Mot de passe:", self.db_password_input)
        
        self.db_name_input = QLineEdit()
        self.db_name_input.setText(self.settings.get('database.database', ''))
        self.db_layout.addRow("Base:", self.db_name_input)
        
        db_group.setLayout(self.db_layout)
        layout.addWidget(db_group)
        
        warning_label = QLabel("⚠️ La modification des paramètres de base de données nécessite un redémarrage")
        warning_label.setStyleSheet("color: #e67e22; margin-top: 10px;")
        layout.addWidget(warning_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        self.toggle_db_fields(self.db_type_combo.currentIndex())
        return widget

    def toggle_db_fields(self, index):
        """Afficher/masquer les champs selon le type de base"""
        if index == 0:  # SQLite
            self.db_path_input.show()
        else:
            self.db_path_input.hide()
    
    def browse_storage_path(self):
        """Browse for storage directory"""
        path = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de stockage")
        if path:
            self.storage_path_input.setText(path)
    
    def browse_sqlite_path(self):
        """Browse for SQLite database file"""
        path, _ = QFileDialog.getSaveFileName(self, "Choisir le fichier SQLite", "", "SQLite DB (*.db)")
        if path:
            self.db_path_input.setText(path)
    
    def save_settings(self):
        """Save all settings"""
        # Storage
        self.settings.set('storage.base_path', self.storage_path_input.text())
        self.settings.set('storage.remote_path', self.remote_storage_input.text())
        
        # Database
        db_types = {0: 'sqlite', 1: 'postgresql', 2: 'mysql'}
        db_type = db_types[self.db_type_combo.currentIndex()]
        self.settings.set('database.type', db_type)
        
        if db_type == 'sqlite':
            self.settings.set('database.path', self.db_path_input.text())
        else:
            self.settings.set('database.host', self.db_host_input.text())
            self.settings.set('database.port', self.db_port_input.value())
            self.settings.set('database.user', self.db_user_input.text())
            self.settings.set('database.password', self.db_password_input.text())
            self.settings.set('database.database', self.db_name_input.text())
        
        # Permissions
        self.settings.set('permissions.allow_file_deletion', self.allow_deletion_cb.isChecked())
        self.settings.set('permissions.allow_folder_deletion', self.allow_folder_deletion_cb.isChecked())
        self.settings.set('permissions.require_confirmation', self.require_confirmation_cb.isChecked())
        
        # UI
        lang_map = {0: 'fr', 1: 'en', 2: 'es'}
        self.settings.set('ui.language', lang_map[self.language_combo.currentIndex()])
        
        theme_map = {0: 'light', 1: 'dark', 2: 'system'}
        self.settings.set('ui.theme', theme_map[self.theme_combo.currentIndex()])
        
        QMessageBox.information(self, "Succès", "Paramètres enregistrés avec succès")
        self.accept()
