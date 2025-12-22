# views/share_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QPushButton, QMessageBox, QGroupBox)
from PySide6.QtCore import Qt
from controllers.sharing_controller import SharingController
from models.folder_share import SharePermission
from models.user import User

class ShareDialog(QDialog):
    """Dialogue pour partager un dossier avec un utilisateur"""
    
    def __init__(self, folder, current_user, db, parent=None):
        super().__init__(parent)
        self.folder = folder
        self.current_user = current_user
        self.db = db
        self.sharing_controller = SharingController(current_user, db)
        
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        """Initialiser l'interface"""
        self.setWindowTitle(f"Partager: {self.folder.name}")
        self.setGeometry(200, 200, 450, 250)
        
        layout = QVBoxLayout()
        
        # Info dossier
        folder_info = QLabel(f"📁 <b>{self.folder.name}</b>")
        folder_info.setStyleSheet("font-size: 14px; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        layout.addWidget(folder_info)
        
        layout.addSpacing(15)
        
        # Sélection utilisateur
        user_group = QGroupBox("Utilisateur")
        user_layout = QVBoxLayout()
        
        self.user_combo = QComboBox()
        user_layout.addWidget(self.user_combo)
        
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)
        
        # Sélection permission
        perm_group = QGroupBox("Permission")
        perm_layout = QVBoxLayout()
        
        self.permission_combo = QComboBox()
        self.permission_combo.addItem("👁️ Lecture seule", SharePermission.READ)
        self.permission_combo.addItem("✏️ Lecture et écriture", SharePermission.WRITE)
        self.permission_combo.addItem("⚙️ Gestion complète", SharePermission.MANAGE)
        perm_layout.addWidget(self.permission_combo)
        
        # Descriptions
        perm_desc = QLabel(
            "<small>"
            "<b>Lecture seule:</b> Consulter les fichiers<br>"
            "<b>Lecture et écriture:</b> Ajouter des fichiers<br>"
            "<b>Gestion complète:</b> Renommer, supprimer"
            "</small>"
        )
        perm_desc.setWordWrap(True)
        perm_desc.setStyleSheet("color: #7f8c8d; padding: 5px;")
        perm_layout.addWidget(perm_desc)
        
        perm_group.setLayout(perm_layout)
        layout.addWidget(perm_group)
        
        layout.addStretch()
        
        # Boutons
        button_layout = QHBoxLayout()
        
        share_btn = QPushButton("Partager")
        share_btn.setStyleSheet("""
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
        share_btn.clicked.connect(self.share)
        button_layout.addWidget(share_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_users(self):
        """Charger la liste des utilisateurs"""
        session = self.db.get_session()
        try:
            # Récupérer tous les utilisateurs sauf l'utilisateur actuel
            users = session.query(User).filter(User.id != self.current_user.id).all()
            
            if not users:
                self.user_combo.addItem("Aucun utilisateur disponible")
                self.user_combo.setEnabled(False)
                return
            
            for user in users:
                self.user_combo.addItem(f"{user.username} ({user.email})", user.id)
                
        finally:
            session.close()
    
    def share(self):
        """Effectuer le partage"""
        if not self.user_combo.isEnabled():
            QMessageBox.warning(self, "Attention", "Aucun utilisateur disponible")
            return
        
        user_id = self.user_combo.currentData()
        permission = self.permission_combo.currentData()
        
        if user_id is None:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un utilisateur")
            return
        
        success, message = self.sharing_controller.share_folder(
            self.folder.id,
            user_id,
            permission
        )
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", message)