# views/manage_shares_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QMessageBox)
from PySide6.QtCore import Qt
from controllers.sharing_controller import SharingController

class ManageSharesDialog(QDialog):
    """Dialogue pour gérer les partages d'un dossier"""
    
    def __init__(self, folder, current_user, db, parent=None):
        super().__init__(parent)
        self.folder = folder
        self.current_user = current_user
        self.db = db
        self.sharing_controller = SharingController(current_user, db)
        
        self.init_ui()
        self.load_shares()
    
    def init_ui(self):
        """Initialiser l'interface"""
        self.setWindowTitle(f"Gérer les partages: {self.folder.name}")
        self.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout()
        
        # Info dossier
        folder_info = QLabel(f"📁 <b>{self.folder.name}</b>")
        folder_info.setStyleSheet("font-size: 14px; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        layout.addWidget(folder_info)
        
        layout.addSpacing(10)
        
        # Titre
        title = QLabel("Utilisateurs ayant accès à ce dossier:")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # Table des partages
        self.shares_table = QTableWidget()
        self.shares_table.setColumnCount(4)
        self.shares_table.setHorizontalHeaderLabels([
            "Utilisateur", "Email", "Permission", "Actions"
        ])
        self.shares_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.shares_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.shares_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.shares_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.shares_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.shares_table)
        
        # Bouton fermer
        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet("""
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
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_shares(self):
        """Charger les partages"""
        self.shares_table.setRowCount(0)
        
        shares = self.sharing_controller.get_folder_shares(self.folder.id)
        
        if not shares:
            return
        
        for share in shares:
            row = self.shares_table.rowCount()
            self.shares_table.insertRow(row)
            
            # Utilisateur
            self.shares_table.setItem(row, 0, QTableWidgetItem(share.user.username))
            
            # Email
            self.shares_table.setItem(row, 1, QTableWidgetItem(share.user.email))
            
            # Permission
            permission_icons = {
                'read': '👁️ Lecture',
                'write': '✏️ Écriture',
                'manage': '⚙️ Gestion'
            }
            perm_text = permission_icons.get(share.permission.value, share.permission.value)
            self.shares_table.setItem(row, 2, QTableWidgetItem(perm_text))
            
            # Bouton supprimer
            remove_btn = QPushButton("🗑️ Retirer")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            remove_btn.clicked.connect(lambda checked, s=share: self.remove_share(s))
            self.shares_table.setCellWidget(row, 3, remove_btn)
    
    def remove_share(self, share):
        """Retirer un partage"""
        reply = QMessageBox.question(
            self,
            'Confirmation',
            f'Voulez-vous retirer l\'accès de {share.user.username} ?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.sharing_controller.unshare_folder(
                self.folder.id,
                share.user_id
            )
            
            if success:
                QMessageBox.information(self, "Succès", message)
                self.load_shares()
            else:
                QMessageBox.critical(self, "Erreur", message)