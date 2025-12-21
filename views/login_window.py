# views/login_window.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QMessageBox, QWidget)
from PySide6.QtCore import Qt
from controllers.auth_controller import AuthController
from database.db_manager import DatabaseManager

class LoginWindow(QDialog):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.auth_controller = AuthController(self.db)
        self.user = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Connexion - Gestionnaire d'Archives")
        self.setFixedSize(400, 450)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Gestionnaire d'Archives Numériques")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Username
        username_label = QLabel("Nom d'utilisateur:")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("Mot de passe:")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.login)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(10)
        
        # Login button
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        
        # Register button
        self.register_btn = QPushButton("Créer un compte")
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.register_btn.clicked.connect(self.open_register)
        layout.addWidget(self.register_btn)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs")
            return
        
        success, result = self.auth_controller.login(username, password)
        
        if success:
            self.user = result
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur de connexion", result)
    
    def open_register(self):
        from views.register_window import RegisterWindow
        
        # Créer et afficher la fenêtre d'inscription
        register_window = RegisterWindow(self.db)
        result = register_window.exec()
        
        # La fenêtre de login reste visible en arrière-plan
        # Après la fermeture du dialogue d'inscription
        if result == QDialog.Accepted:
            QMessageBox.information(
                self, 
                "Succès", 
                "Compte créé avec succès! Vous pouvez maintenant vous connecter."
            )
            # Optionnel: pré-remplir le nom d'utilisateur
            if hasattr(register_window, 'username_input'):
                self.username_input.setText(register_window.username_input.text())
                self.password_input.setFocus()