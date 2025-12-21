

# views/settings_window.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QCheckBox,
                               QTabWidget, QWidget, QFileDialog, QMessageBox,
                               QGroupBox, QFormLayout,QSpinBox)
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
        
        # Tabs
        tabs = QTabWidget()
        
        # General tab
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "Général")
        
        # Storage tab
        storage_tab = self.create_storage_tab()
        tabs.addTab(storage_tab, "Stockage")
        
        # Database tab
        database_tab = self.create_database_tab()
        tabs.addTab(database_tab, "Base de données")
        
        # Permissions tab
        permissions_tab = self.create_permissions_tab()
        tabs.addTab(permissions_tab, "Droits d'accès")
        
        # Appearance tab
        appearance_tab = self.create_appearance_tab()
        tabs.addTab(appearance_tab, "Apparence")
        
        layout.addWidget(tabs)
        
        # Action buttons
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
    
    def create_general_tab(self):
        """Create general settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Language
        lang_group = QGroupBox("Langue")
        lang_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Français", "English", "Español"])
        current_lang = self.settings.get('ui.language', 'fr')
        lang_map = {'fr': 0, 'en': 1, 'es': 2}
        self.language_combo.setCurrentIndex(lang_map.get(current_lang, 0))
        
        lang_layout.addRow("Langue de l'interface:", self.language_combo)
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_storage_tab(self):
        """Create storage settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        storage_group = QGroupBox("Emplacement de stockage")
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
        
        # Champ SQLite
        self.db_path_input = QLineEdit()
        self.db_path_input.setText(self.settings.get('database.path', ''))
        self.db_layout.addRow("Chemin:", self.db_path_input)
        
        # Champs serveur (PostgreSQL/MySQL)
        self.db_host_input = QLineEdit()
        self.db_host_input.setText(self.settings.get('database.host', 'localhost'))
        self.db_layout.addRow("Hôte:", self.db_host_input)
        
        self.db_port_input = QSpinBox() 
        self.db_port_input.setRange(1, 65535) # ports valides
        self.db_port_input.setValue(int(self.settings.get('database.port', 5432))) # valeur par défaut
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
        
        warning_label = QLabel(
            "⚠️ La modification des paramètres de base de données nécessite un redémarrage"
        )
        warning_label.setStyleSheet("color: #e67e22; margin-top: 10px;")
        layout.addWidget(warning_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        # Initialiser l’affichage selon le type
        self.toggle_db_fields(self.db_type_combo.currentIndex())
        
        return widget

    def toggle_db_fields(self, index):
        """Afficher/masquer les champs selon le type de base"""
        if index == 0:  # SQLite
            self.db_path_input.show()
            self.db_host_input.hide()
            self.db_port_input.hide()
            self.db_user_input.hide()
            self.db_password_input.hide()
            self.db_name_input.hide()
        else:  # PostgreSQL ou MySQL
            self.db_path_input.hide()
            self.db_host_input.show()
            self.db_port_input.show()
            self.db_user_input.show()
            self.db_password_input.show()
            self.db_name_input.show()

    def create_permissions_tab(self):
        """Create permissions settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        perm_group = QGroupBox("Droits d'accès")
        perm_layout = QVBoxLayout()
        
        self.allow_deletion_cb = QCheckBox("Autoriser la suppression de fichiers")
        self.allow_deletion_cb.setChecked(
            self.settings.get('permissions.allow_file_deletion', True)
        )
        perm_layout.addWidget(self.allow_deletion_cb)
        
        self.allow_folder_deletion_cb = QCheckBox("Autoriser la suppression de dossiers")
        self.allow_folder_deletion_cb.setChecked(
            self.settings.get('permissions.allow_folder_deletion', True)
        )
        perm_layout.addWidget(self.allow_folder_deletion_cb)
        
        self.require_confirmation_cb = QCheckBox("Demander confirmation pour les suppressions")
        self.require_confirmation_cb.setChecked(
            self.settings.get('permissions.require_confirmation', True)
        )
        perm_layout.addWidget(self.require_confirmation_cb)
        
        perm_group.setLayout(perm_layout)
        layout.addWidget(perm_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_appearance_tab(self):
        """Create appearance settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        theme_group = QGroupBox("Thème")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Clair", "Sombre", "Système"])
        current_theme = self.settings.get('ui.theme', 'light')
        theme_map = {'light': 0, 'dark': 1, 'system': 2}
        self.theme_combo.setCurrentIndex(theme_map.get(current_theme, 0))
        
        theme_layout.addRow("Thème d'affichage:", self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def browse_storage_path(self):
        """Browse for storage directory"""
        path = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de stockage")
        if path:
            self.storage_path_input.setText(path)
    
    def save_settings(self):
        """Save all settings"""
        # Storage
        self.settings.set('storage.base_path', self.storage_path_input.text())
        
        # Database
        db_types = {0: 'sqlite', 1: 'postgresql', 2: 'mysql'}
        db_type = db_types[self.db_type_combo.currentIndex()]
        self.settings.set('database.type', db_type)
        
        if db_type == 'sqlite':
            self.settings.set('database.path', self.db_path_input.text())
        else:
            self.settings.set('database.host', self.db_host_input.text())
            self.settings.set('database.port', self.db_port_input.text())
            self.settings.set('database.user', self.db_user_input.text())
            self.settings.set('database.password', self.db_password_input.text())
            self.settings.set('database.database', self.db_name_input.text())
        
        # Permissions
        self.settings.set('permissions.allow_file_deletion', 
                        self.allow_deletion_cb.isChecked())
        self.settings.set('permissions.allow_folder_deletion', 
                        self.allow_folder_deletion_cb.isChecked())
        self.settings.set('permissions.require_confirmation', 
                        self.require_confirmation_cb.isChecked())
        
        # UI
        lang_map = {0: 'fr', 1: 'en', 2: 'es'}
        self.settings.set('ui.language', lang_map[self.language_combo.currentIndex()])
        
        theme_map = {0: 'light', 1: 'dark', 2: 'system'}
        self.settings.set('ui.theme', theme_map[self.theme_combo.currentIndex()])
        
        QMessageBox.information(self, "Succès", "Paramètres enregistrés avec succès")
        self.accept()


   