
# views/register_window.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                               QPushButton, QMessageBox)
from PySide6.QtCore import Qt
from controllers.auth_controller import AuthController
import re
from database.db_manager import DatabaseManager

class RegisterWindow(QDialog):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.auth_controller = AuthController(db)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Inscription - Gestionnaire d'Archives")
        self.setFixedSize(450, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Créer un nouveau compte")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Username
        username_label = QLabel("Nom d'utilisateur:")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choisissez un nom d'utilisateur")
        layout.addWidget(self.username_input)
        
        # Email
        email_label = QLabel("Email:")
        layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("votre@email.com")
        layout.addWidget(self.email_input)
        
        # Password
        password_label = QLabel("Mot de passe:")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Minimum 6 caractères")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # Confirm Password
        confirm_label = QLabel("Confirmer le mot de passe:")
        layout.addWidget(confirm_label)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Retapez votre mot de passe")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)
        
        layout.addSpacing(10)
        
        # Register button
        self.register_btn = QPushButton("S'inscrire")
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
        self.register_btn.clicked.connect(self.register)
        layout.addWidget(self.register_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        # Validation
        if not username or not email or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs")
            return
        
        if len(username) < 3:
            QMessageBox.warning(self, "Erreur", 
                              "Le nom d'utilisateur doit contenir au moins 3 caractères")
            return
        
        if not self.validate_email(email):
            QMessageBox.warning(self, "Erreur", "Adresse email invalide")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Erreur", 
                              "Le mot de passe doit contenir au moins 6 caractères")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Erreur", 
                              "Les mots de passe ne correspondent pas")
            return
        
        # Register user
        success, message = self.auth_controller.register(username, email, password)
        
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur d'inscription", message)