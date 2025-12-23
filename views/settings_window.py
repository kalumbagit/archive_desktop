# views/settings_window.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QCheckBox,
                               QTabWidget, QWidget, QFileDialog,
                               QGroupBox, QFormLayout, QSpinBox, QStackedWidget,
                               QProgressDialog)
from PySide6.QtCore import Qt, QThread, Signal
from config.settings import Settings
import sys
from controllers.cloud_storage import CloudStorageService
from pathlib import Path
from utils.alert_dialog import AlertDialog

class ConnectionTestThread(QThread):
    """Thread pour tester la connexion sans bloquer l'interface"""
    finished = Signal(bool, str)
    
    def __init__(self, test_type, *args):
        super().__init__()
        self.test_type = test_type
        self.args = args
    
    def run(self):
        if self.test_type == 'database':
            success, message = self.test_database_connection(*self.args)
        elif self.test_type == 'cloud':
            success, message = CloudStorageService.test_connection(*self.args)
        else:
            success, message = False, "Type de test inconnu"
        
        self.finished.emit(success, message)
    
    def test_database_connection(self, db_type, **config):
        """Tester la connexion à la base de données"""
        try:
            from sqlalchemy import create_engine
            
            if db_type == 'postgresql':
                url = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            elif db_type == 'mysql':
                url = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            else:
                return False, "Type de base de données non supporté pour le test"
            
            engine = create_engine(url, pool_pre_ping=True)
            connection = engine.connect()
            connection.close()
            engine.dispose()
            
            return True, f"Connexion {db_type.upper()} réussie"
            
        except ImportError as e:
            return False, f"Bibliothèque manquante: {str(e)}"
        except Exception as e:
            return False, f"Erreur de connexion: {str(e)}"

class SettingsWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.settings = Settings()
        self.test_thread = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Paramètres")
        self.setGeometry(200, 200, 700, 600)
        
        layout = QVBoxLayout()
        
        # Tabs
        tabs = QTabWidget()
        
        # General tab
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "Général")
        
        # Storage tab
        storage_tab = self.create_storage_tab()
        tabs.addTab(storage_tab, "Stockage")
        
        # Cloud tab
        cloud_tab = self.create_cloud_tab()
        tabs.addTab(cloud_tab, "☁️ Cloud")
        
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
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
            }
        """)
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
        
        info_label = QLabel("💡 Les fichiers seront stockés dans ce répertoire")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        storage_layout.addWidget(info_label)
        
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_cloud_tab(self):
        """Create cloud storage tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Activation du cloud
        self.cloud_enabled_cb = QCheckBox("Activer le stockage cloud")
        self.cloud_enabled_cb.setChecked(self.settings.get('storage.cloud_enabled', False))
        self.cloud_enabled_cb.toggled.connect(self.toggle_cloud_fields)
        layout.addWidget(self.cloud_enabled_cb)
        
        # Container pour les champs cloud
        self.cloud_container = QWidget()
        cloud_layout = QVBoxLayout()
        
        # Copie de sauvegarde
        self.cloud_backup_cb = QCheckBox("Sauvegarder une copie dans le cloud")
        self.cloud_backup_cb.setChecked(self.settings.get('storage.cloud_backup_enabled', False))
        self.cloud_backup_cb.setToolTip("Les fichiers seront stockés localement ET dans le cloud")
        cloud_layout.addWidget(self.cloud_backup_cb)
        
        cloud_layout.addSpacing(10)
        
        # Type de cloud
        type_group = QGroupBox("Type de stockage cloud")
        type_layout = QVBoxLayout()
        
        self.cloud_type_combo = QComboBox()
        self.cloud_type_combo.addItem("AWS S3", "aws_s3")
        self.cloud_type_combo.addItem("Azure Blob Storage", "azure")
        self.cloud_type_combo.addItem("Google Cloud Storage", "google_cloud")
        self.cloud_type_combo.addItem("FTP/SFTP", "ftp")
        
        current_cloud = self.settings.get('storage.cloud_type', 'aws_s3')
        cloud_map = {'aws_s3': 0, 'azure': 1, 'google_cloud': 2, 'ftp': 3}
        self.cloud_type_combo.setCurrentIndex(cloud_map.get(current_cloud, 0))
        self.cloud_type_combo.currentIndexChanged.connect(self.change_cloud_config)
        
        type_layout.addWidget(self.cloud_type_combo)
        type_group.setLayout(type_layout)
        cloud_layout.addWidget(type_group)
        
        # Stack widget pour les configurations
        self.cloud_config_stack = QStackedWidget()
        
        # AWS S3
        self.cloud_config_stack.addWidget(self.create_aws_config())
        
        # Azure
        self.cloud_config_stack.addWidget(self.create_azure_config())
        
        # Google Cloud
        self.cloud_config_stack.addWidget(self.create_google_config())
        
        # FTP
        self.cloud_config_stack.addWidget(self.create_ftp_config())
        
        cloud_layout.addWidget(self.cloud_config_stack)
        
        # Test connection button
        test_cloud_btn = QPushButton("🔌 Tester la connexion")
        test_cloud_btn.setStyleSheet("""
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
        test_cloud_btn.clicked.connect(self.test_cloud_connection)
        cloud_layout.addWidget(test_cloud_btn)
        
        self.cloud_container.setLayout(cloud_layout)
        layout.addWidget(self.cloud_container)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        # Initialiser l'affichage
        self.toggle_cloud_fields(self.cloud_enabled_cb.isChecked())
        self.change_cloud_config(self.cloud_type_combo.currentIndex())
        
        return widget
    
    def create_aws_config(self):
        """Configuration AWS S3"""
        widget = QWidget()
        layout = QFormLayout()
        
        self.aws_access_key = QLineEdit()
        self.aws_access_key.setText(self.settings.get('storage.cloud_config.aws_s3.access_key', ''))
        layout.addRow("Access Key ID:", self.aws_access_key)
        
        self.aws_secret_key = QLineEdit()
        self.aws_secret_key.setEchoMode(QLineEdit.Password)
        self.aws_secret_key.setText(self.settings.get('storage.cloud_config.aws_s3.secret_key', ''))
        layout.addRow("Secret Access Key:", self.aws_secret_key)
        
        self.aws_bucket = QLineEdit()
        self.aws_bucket.setText(self.settings.get('storage.cloud_config.aws_s3.bucket_name', ''))
        layout.addRow("Bucket Name:", self.aws_bucket)
        
        self.aws_region = QLineEdit()
        self.aws_region.setText(self.settings.get('storage.cloud_config.aws_s3.region', 'us-east-1'))
        self.aws_region.setPlaceholderText("us-east-1")
        layout.addRow("Region:", self.aws_region)
        
        widget.setLayout(layout)
        return widget
    
    def create_azure_config(self):
        """Configuration Azure"""
        widget = QWidget()
        layout = QFormLayout()
        
        self.azure_account = QLineEdit()
        self.azure_account.setText(self.settings.get('storage.cloud_config.azure.account_name', ''))
        layout.addRow("Account Name:", self.azure_account)
        
        self.azure_key = QLineEdit()
        self.azure_key.setEchoMode(QLineEdit.Password)
        self.azure_key.setText(self.settings.get('storage.cloud_config.azure.account_key', ''))
        layout.addRow("Account Key:", self.azure_key)
        
        self.azure_container = QLineEdit()
        self.azure_container.setText(self.settings.get('storage.cloud_config.azure.container_name', ''))
        layout.addRow("Container Name:", self.azure_container)
        
        widget.setLayout(layout)
        return widget
    
    def create_google_config(self):
        """Configuration Google Cloud"""
        widget = QWidget()
        layout = QFormLayout()
        
        self.google_project = QLineEdit()
        self.google_project.setText(self.settings.get('storage.cloud_config.google_cloud.project_id', ''))
        layout.addRow("Project ID:", self.google_project)
        
        self.google_bucket = QLineEdit()
        self.google_bucket.setText(self.settings.get('storage.cloud_config.google_cloud.bucket_name', ''))
        layout.addRow("Bucket Name:", self.google_bucket)
        
        creds_layout = QHBoxLayout()
        self.google_creds = QLineEdit()
        self.google_creds.setText(self.settings.get('storage.cloud_config.google_cloud.credentials_file', ''))
        creds_layout.addWidget(self.google_creds)
        
        browse_creds = QPushButton("...")
        browse_creds.clicked.connect(self.browse_google_creds)
        creds_layout.addWidget(browse_creds)
        
        layout.addRow("Credentials File:", creds_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_ftp_config(self):
        """Configuration FTP"""
        widget = QWidget()
        layout = QFormLayout()
        
        self.ftp_host = QLineEdit()
        self.ftp_host.setText(self.settings.get('storage.cloud_config.ftp.host', ''))
        layout.addRow("Host:", self.ftp_host)
        
        self.ftp_port = QSpinBox()
        self.ftp_port.setRange(1, 65535)
        self.ftp_port.setValue(int(self.settings.get('storage.cloud_config.ftp.port', 21)))
        layout.addRow("Port:", self.ftp_port)
        
        self.ftp_user = QLineEdit()
        self.ftp_user.setText(self.settings.get('storage.cloud_config.ftp.username', ''))
        layout.addRow("Username:", self.ftp_user)
        
        self.ftp_password = QLineEdit()
        self.ftp_password.setEchoMode(QLineEdit.Password)
        self.ftp_password.setText(self.settings.get('storage.cloud_config.ftp.password', ''))
        layout.addRow("Password:", self.ftp_password)
        
        self.ftp_path = QLineEdit()
        self.ftp_path.setText(self.settings.get('storage.cloud_config.ftp.remote_path', '/'))
        layout.addRow("Remote Path:", self.ftp_path)
        
        widget.setLayout(layout)
        return widget
    
    def toggle_cloud_fields(self, enabled):
        """Activer/désactiver les champs cloud"""
        self.cloud_container.setEnabled(enabled)
    
    def change_cloud_config(self, index):
        """Changer la configuration cloud affichée"""
        self.cloud_config_stack.setCurrentIndex(index)
    
    def browse_google_creds(self):
        """Parcourir pour le fichier credentials Google"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le fichier credentials",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        if file_path:
            self.google_creds.setText(file_path)
    
    def test_cloud_connection(self):
        """Tester la connexion cloud"""
        cloud_type = self.cloud_type_combo.currentData()
        
        # Récupérer la configuration selon le type
        if cloud_type == 'aws_s3':
            config = {
                'access_key': self.aws_access_key.text(),
                'secret_key': self.aws_secret_key.text(),
                'bucket_name': self.aws_bucket.text(),
                'region': self.aws_region.text()
            }
        elif cloud_type == 'azure':
            config = {
                'account_name': self.azure_account.text(),
                'account_key': self.azure_key.text(),
                'container_name': self.azure_container.text()
            }
        elif cloud_type == 'google_cloud':
            config = {
                'project_id': self.google_project.text(),
                'bucket_name': self.google_bucket.text(),
                'credentials_file': self.google_creds.text()
            }
        elif cloud_type == 'ftp':
            config = {
                'host': self.ftp_host.text(),
                'port': self.ftp_port.value(),
                'username': self.ftp_user.text(),
                'password': self.ftp_password.text(),
                'remote_path': self.ftp_path.text()
            }
        else:
            AlertDialog.warning(self, "Erreur", "Type de cloud non supporté")
            return
        
        # Créer et lancer le thread de test
        self.test_thread = ConnectionTestThread('cloud', cloud_type, config)
        self.test_thread.finished.connect(self.on_cloud_test_finished)
        
        # Afficher un dialogue de progression
        self.progress = QProgressDialog("Test de connexion en cours...", None, 0, 0, self)
        self.progress.setWindowTitle("Test de connexion")
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.show()
        
        self.test_thread.start()
    
    def on_cloud_test_finished(self, success, message):
        """Gérer le résultat du test cloud"""
        self.progress.close()
        
        if success:
            AlertDialog.information(self, "Succès", message)
            # Activer automatiquement le backup cloud si le test réussit
            if not self.cloud_backup_cb.isChecked():
                reply = AlertDialog.question(
                    self,
                    "Activer la sauvegarde cloud",
                    "La connexion a réussi. Voulez-vous activer la sauvegarde automatique dans le cloud?"
                )
                if reply == True:
                    self.cloud_backup_cb.setChecked(True)
        else:
            AlertDialog.error(self, "Échec", message)
    
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
        
        # Champ SQLite avec parcourir
        sqlite_layout = QHBoxLayout()
        self.db_path_input = QLineEdit()
        self.db_path_input.setText(self.settings.get('database.path', ''))
        sqlite_layout.addWidget(self.db_path_input)
        
        self.db_browse_btn = QPushButton("Parcourir")
        self.db_browse_btn.clicked.connect(self.browse_database_path)
        sqlite_layout.addWidget(self.db_browse_btn)
        
        self.db_path_widget = QWidget()
        self.db_path_widget.setLayout(sqlite_layout)
        self.db_layout.addRow("Chemin:", self.db_path_widget)
        
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
        
        # Test connection button
        test_db_btn = QPushButton("🔌 Tester la connexion")
        test_db_btn.setStyleSheet("""
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
        test_db_btn.clicked.connect(self.test_database_connection)
        layout.addWidget(test_db_btn)
        
        warning_label = QLabel(
            "⚠️ La modification des paramètres de base de données nécessite un redémarrage"
        )
        warning_label.setStyleSheet("color: #e67e22; margin-top: 10px;")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        # Initialiser l'affichage selon le type
        self.toggle_db_fields(self.db_type_combo.currentIndex())
        
        return widget
    
    def browse_database_path(self):
        """Parcourir pour le chemin de la base SQLite"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Choisir l'emplacement de la base de données",
            self.db_path_input.text() or str(Path.home() / '.archive_manager' / 'archives.db'),
            "Base de données SQLite (*.db);;Tous les fichiers (*.*)"
        )
        if file_path:
            self.db_path_input.setText(file_path)
    
    def toggle_db_fields(self, index):
        """Afficher/masquer les champs selon le type de base"""
        if index == 0:  # SQLite
            self.db_path_widget.show()
            self.db_host_input.hide()
            self.db_port_input.hide()
            self.db_user_input.hide()
            self.db_password_input.hide()
            self.db_name_input.hide()
            
            # Masquer les labels aussi
            for i in range(self.db_layout.rowCount()):
                label = self.db_layout.itemAt(i, QFormLayout.LabelRole)
                if label and label.widget():
                    label_text = label.widget().text()
                    if label_text in ["Hôte:", "Port:", "Utilisateur:", "Mot de passe:", "Base:"]:
                        label.widget().hide()
                        field = self.db_layout.itemAt(i, QFormLayout.FieldRole)
                        if field and field.widget():
                            field.widget().hide()
        else:  # PostgreSQL ou MySQL
            self.db_path_widget.hide()
            self.db_host_input.show()
            self.db_port_input.show()
            self.db_user_input.show()
            self.db_password_input.show()
            self.db_name_input.show()
            
            # Afficher les labels
            for i in range(self.db_layout.rowCount()):
                label = self.db_layout.itemAt(i, QFormLayout.LabelRole)
                if label and label.widget():
                    label_text = label.widget().text()
                    if label_text in ["Hôte:", "Port:", "Utilisateur:", "Mot de passe:", "Base:"]:
                        label.widget().show()
                        field = self.db_layout.itemAt(i, QFormLayout.FieldRole)
                        if field and field.widget():
                            field.widget().show()
    
    def test_database_connection(self):
        """Tester la connexion à la base de données"""
        db_types = {0: 'sqlite', 1: 'postgresql', 2: 'mysql'}
        db_type = db_types[self.db_type_combo.currentIndex()]
        
        if db_type == 'sqlite':
            AlertDialog.information(
                self,
                "SQLite",
                "SQLite ne nécessite pas de connexion réseau.\n"
                "Le fichier sera créé automatiquement au démarrage."
            )
            return
        
        config = {
            'host': self.db_host_input.text(),
            'port': self.db_port_input.value(),
            'user': self.db_user_input.text(),
            'password': self.db_password_input.text(),
            'database': self.db_name_input.text()
        }
        
        # Créer et lancer le thread de test
        self.test_thread = ConnectionTestThread('database', db_type, **config)
        self.test_thread.finished.connect(self.on_db_test_finished)
        
        self.progress = QProgressDialog("Test de connexion en cours...", None, 0, 0, self)
        self.progress.setWindowTitle("Test de connexion")
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.show()
        
        self.test_thread.start()
    
    def on_db_test_finished(self, success, message):
        """Gérer le résultat du test de base de données"""
        self.progress.close()
        
        if success:
            AlertDialog.information(self, "Succès", message)
        else:
            AlertDialog.error(self, "Échec", message)
    
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
        db_changed = False
        
        # Storage
        self.settings.set('storage.base_path', self.storage_path_input.text())
        
        # Cloud settings
        self.settings.set('storage.cloud_enabled', self.cloud_enabled_cb.isChecked())
        self.settings.set('storage.cloud_backup_enabled', self.cloud_backup_cb.isChecked())
        
        cloud_type = self.cloud_type_combo.currentData()
        self.settings.set('storage.cloud_type', cloud_type)
        
        # Save cloud config based on type
        if cloud_type == 'aws_s3':
            self.settings.set('storage.cloud_config.aws_s3.access_key', self.aws_access_key.text())
            self.settings.set('storage.cloud_config.aws_s3.secret_key', self.aws_secret_key.text())
            self.settings.set('storage.cloud_config.aws_s3.bucket_name', self.aws_bucket.text())
            self.settings.set('storage.cloud_config.aws_s3.region', self.aws_region.text())
        elif cloud_type == 'azure':
            self.settings.set('storage.cloud_config.azure.account_name', self.azure_account.text())
            self.settings.set('storage.cloud_config.azure.account_key', self.azure_key.text())
            self.settings.set('storage.cloud_config.azure.container_name', self.azure_container.text())
        elif cloud_type == 'google_cloud':
            self.settings.set('storage.cloud_config.google_cloud.project_id', self.google_project.text())
            self.settings.set('storage.cloud_config.google_cloud.bucket_name', self.google_bucket.text())
            self.settings.set('storage.cloud_config.google_cloud.credentials_file', self.google_creds.text())
        elif cloud_type == 'ftp':
            self.settings.set('storage.cloud_config.ftp.host', self.ftp_host.text())
            self.settings.set('storage.cloud_config.ftp.port', self.ftp_port.value())
            self.settings.set('storage.cloud_config.ftp.username', self.ftp_user.text())
            self.settings.set('storage.cloud_config.ftp.password', self.ftp_password.text())
            self.settings.set('storage.cloud_config.ftp.remote_path', self.ftp_path.text())
        
        # Database
        db_types = {0: 'sqlite', 1: 'postgresql', 2: 'mysql'}
        new_db_type = db_types[self.db_type_combo.currentIndex()]
        old_db_type = self.settings.get('database.type')
        
        if new_db_type != old_db_type:
            db_changed = True
        
        self.settings.set('database.type', new_db_type)
        
        if new_db_type == 'sqlite':
            new_path = self.db_path_input.text()
            old_path = self.settings.get('database.path')
            if new_path != old_path:
                db_changed = True
            self.settings.set('database.path', new_path)
        else:
            self.settings.set('database.host', self.db_host_input.text())
            self.settings.set('database.port', self.db_port_input.value())
            self.settings.set('database.user', self.db_user_input.text())
            self.settings.set('database.password', self.db_password_input.text())
            self.settings.set('database.database', self.db_name_input.text())
            db_changed = True  # Toujours redémarrer pour les bases distantes
        
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
        
        # Message de confirmation
        if db_changed:
            reply = AlertDialog.question(
                self,
                "Redémarrage requis",
                "Les paramètres de base de données ont été modifiés.\n\n"
                "L'application doit redémarrer pour appliquer ces changements.\n"
                "Voulez-vous redémarrer maintenant?"
            )
            
            if reply == True:
                self.accept()
                # Redémarrer l'application
                import os
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                AlertDialog.error(
                    self,
                    "Attention",
                    "Les changements de base de données ne seront effectifs qu'au prochain démarrage."
                )
                self.accept()
        else:
            AlertDialog.information(self, "Succès", "Paramètres enregistrés avec succès")
            self.accept()