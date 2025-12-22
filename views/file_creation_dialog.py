# views/file_creation_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QTextEdit,
                               QMessageBox, QGroupBox)
from PySide6.QtCore import Qt

class FileCreationDialog(QDialog):
    """Dialogue pour créer un nouveau fichier"""
    
    def __init__(self, folder, parent=None):
        super().__init__(parent)
        self.folder = folder
        self.file_name = None
        self.file_type = None
        self.file_content = ""
        
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        self.setWindowTitle(f"Créer un fichier dans: {self.folder.name}")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        
        # Info sur le dossier
        folder_info = QLabel(f"📁 Dossier: <b>{self.folder.name}</b>")
        folder_info.setStyleSheet("color: #2c3e50; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        layout.addWidget(folder_info)
        
        layout.addSpacing(10)
        
        # Nom du fichier
        name_group = QGroupBox("Nom du fichier")
        name_layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: mon_document.txt")
        name_layout.addWidget(self.name_input)
        
        name_hint = QLabel("💡 Incluez l'extension (.txt, .md, .json, .csv, etc.)")
        name_hint.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        name_layout.addWidget(name_hint)
        
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)
        
        # Type de fichier
        type_group = QGroupBox("Type de fichier")
        type_layout = QVBoxLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Fichier vide",
            "Fichier texte",
            "Fichier Markdown",
            "Fichier JSON",
            "Fichier CSV"
        ])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Contenu (optionnel)
        content_group = QGroupBox("Contenu initial (optionnel)")
        content_layout = QVBoxLayout()
        
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Saisir le contenu du fichier...")
        self.content_edit.setEnabled(False)  # Désactivé par défaut
        content_layout.addWidget(self.content_edit)
        
        content_group.setLayout(content_layout)
        layout.addWidget(content_group)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton("Créer")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        create_btn.clicked.connect(self.create_file)
        button_layout.addWidget(create_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_type_changed(self, type_text):
        """Gérer le changement de type de fichier"""
        if type_text == "Fichier vide":
            self.content_edit.setEnabled(False)
            self.content_edit.clear()
            # Suggérer une extension par défaut
            if not self.name_input.text():
                self.name_input.setPlaceholderText("Ex: nouveau_fichier.txt")
        else:
            self.content_edit.setEnabled(True)
            
            # Suggérer une extension et un template selon le type
            if type_text == "Fichier texte":
                self.name_input.setPlaceholderText("Ex: document.txt")
                self.content_edit.setPlaceholderText("Votre texte ici...")
            elif type_text == "Fichier Markdown":
                self.name_input.setPlaceholderText("Ex: readme.md")
                template = "# Titre\n\n## Section 1\n\nContenu...\n\n## Section 2\n\nPlus de contenu..."
                self.content_edit.setPlaceholderText(template)
            elif type_text == "Fichier JSON":
                self.name_input.setPlaceholderText("Ex: data.json")
                template = '{\n  "nom": "valeur",\n  "liste": [1, 2, 3],\n  "objet": {\n    "cle": "valeur"\n  }\n}'
                self.content_edit.setPlaceholderText(template)
            elif type_text == "Fichier CSV":
                self.name_input.setPlaceholderText("Ex: donnees.csv")
                template = "Colonne1,Colonne2,Colonne3\nValeur1,Valeur2,Valeur3\nValeur4,Valeur5,Valeur6"
                self.content_edit.setPlaceholderText(template)
    
    def create_file(self):
        """Valider et créer le fichier"""
        file_name = self.name_input.text().strip()
        
        # Validation du nom
        if not file_name:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez saisir un nom de fichier"
            )
            return
        
        # Vérifier que le nom a une extension
        if '.' not in file_name:
            QMessageBox.warning(
                self,
                "Erreur",
                "Le nom du fichier doit inclure une extension\n(ex: .txt, .md, .json, etc.)"
            )
            return
        
        # Vérifier les caractères invalides
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in file_name for char in invalid_chars):
            QMessageBox.warning(
                self,
                "Erreur",
                f"Le nom du fichier ne peut pas contenir: / \\ : * ? \" < > |"
            )
            return
        
        # Récupérer le contenu
        content = self.content_edit.toPlainText()
        
        # Déterminer le type de fichier
        type_text = self.type_combo.currentText()
        if type_text == "Fichier vide":
            self.file_type = 'empty'
            self.file_content = ""
        elif type_text == "Fichier texte":
            self.file_type = 'text'
            self.file_content = content
        elif type_text == "Fichier Markdown":
            self.file_type = 'markdown'
            self.file_content = content
        elif type_text == "Fichier JSON":
            self.file_type = 'json'
            self.file_content = content
            # Valider le JSON si du contenu est fourni
            if content:
                import json
                try:
                    json.loads(content)
                except json.JSONDecodeError as e:
                    reply = QMessageBox.question(
                        self,
                        "JSON invalide",
                        f"Le JSON semble invalide:\n{str(e)}\n\nVoulez-vous créer le fichier quand même?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
        elif type_text == "Fichier CSV":
            self.file_type = 'csv'
            self.file_content = content
        
        self.file_name = file_name
        self.accept()
    
    def get_file_info(self):
        """Retourner les informations du fichier créé"""
        return {
            'name': self.file_name,
            'type': self.file_type,
            'content': self.file_content
        }