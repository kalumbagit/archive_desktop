# =============================================================================
# FICHIER 1: views/preview_window.py - COMPLET
# =============================================================================
"""
views/preview_window.py
Fenêtre de prévisualisation des fichiers
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTextEdit, QScrollArea, QWidget,
                               QMessageBox, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from utils.preview_generator import PreviewGenerator
from pathlib import Path
import os
import subprocess
import platform

class PreviewWindow(QDialog):
    """Fenêtre de prévisualisation des fichiers"""
    
    def __init__(self, file_obj, parent=None):
        """
        Initialiser la fenêtre de prévisualisation
        
        Args:
            file_obj: Objet File à prévisualiser
            parent: Widget parent
        """
        super().__init__(parent)
        self.file = file_obj
        self.parent_window = parent
        self.preview_gen = PreviewGenerator()
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        self.setWindowTitle(f"Prévisualisation - {self.file.name}")
        self.setGeometry(150, 150, 900, 700)
        
        layout = QVBoxLayout()
        
        # En-tête avec informations du fichier
        info_widget = self.create_info_header()
        layout.addWidget(info_widget)
        
        # Contenu de prévisualisation
        preview_widget = self.create_preview_content()
        layout.addWidget(preview_widget)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        open_btn = QPushButton("Ouvrir avec l'application par défaut")
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        open_btn.clicked.connect(self.open_with_default)
        button_layout.addWidget(open_btn)
        
        download_btn = QPushButton("Télécharger")
        download_btn.setStyleSheet("""
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
        download_btn.clicked.connect(self.download_file)
        button_layout.addWidget(download_btn)
        
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
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_info_header(self):
        """Créer l'en-tête avec les informations du fichier"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Nom du fichier
        name_label = QLabel(f"📄 {self.file.name}")
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(name_label)
        
        # Détails du fichier
        file_info = self.preview_gen.get_file_info(self.file.file_path)
        
        details = QLabel(
            f"Type: {file_info['extension']} | "
            f"Taille: {file_info['size_formatted']} | "
            f"Modifié: {self._format_timestamp(file_info['modified'])}"
        )
        details.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(details)
        
        # Chemin du fichier
        path_label = QLabel(f"Emplacement: {self.file.file_path}")
        path_label.setStyleSheet("color: #95a5a6; font-size: 11px; font-style: italic;")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)
        
        widget.setLayout(layout)
        return widget
    
    def create_preview_content(self):
        """Créer le contenu de prévisualisation selon le type de fichier"""
        file_type = self.preview_gen.get_file_type(self.file.file_path)
        
        if file_type == 'image':
            return self.create_image_preview()
        elif file_type == 'text':
            return self.create_text_preview()
        elif file_type == 'pdf':
            return self.create_pdf_preview()
        else:
            return self.create_no_preview()
    
    def create_image_preview(self):
        """Créer la prévisualisation d'une image"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #2c3e50;")
        
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        
        try:
            pixmap = QPixmap(self.file.file_path)
            
            if pixmap.isNull():
                label.setText("❌ Impossible de charger l'image")
                label.setStyleSheet("color: white; font-size: 14px;")
            else:
                # Redimensionner si trop grand
                if pixmap.width() > 800 or pixmap.height() > 600:
                    pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                label.setPixmap(pixmap)
        except Exception as e:
            label.setText(f"❌ Erreur lors du chargement de l'image:\n{str(e)}")
            label.setStyleSheet("color: white; font-size: 14px;")
        
        scroll.setWidget(label)
        return scroll
    
    def create_text_preview(self):
        """Créer la prévisualisation d'un fichier texte"""
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier New", 10))
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                padding: 10px;
            }
        """)
        
        content = self.preview_gen.extract_text_preview(self.file.file_path, max_chars=10000)
        
        if content:
            text_edit.setPlainText(content)
            
            # Ajouter une note si le fichier est tronqué
            if len(content) >= 10000:
                text_edit.append("\n\n--- Aperçu limité aux 10 000 premiers caractères ---")
        else:
            text_edit.setPlainText("❌ Impossible de lire le contenu du fichier.\n\n"
                                  "Le fichier pourrait être dans un format non supporté ou corrompu.")
        
        return text_edit
    
    def create_pdf_preview(self):
        """Créer la prévisualisation d'un PDF"""
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Arial", 10))
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                padding: 15px;
            }
        """)
        
        content = self.preview_gen.extract_pdf_preview(self.file.file_path, max_pages=3)
        
        if content:
            text_edit.setPlainText(content)
            text_edit.append("\n\n" + "="*50)
            text_edit.append("📄 Aperçu limité aux 3 premières pages")
            text_edit.append("Pour voir le document complet, cliquez sur 'Ouvrir avec l'application par défaut'")
            text_edit.append("="*50)
        else:
            text_edit.setPlainText("❌ Impossible de lire le contenu du PDF.\n\n"
                                  "Raisons possibles:\n"
                                  "- Le PDF est protégé par mot de passe\n"
                                  "- Le PDF est corrompu\n"
                                  "- Le PDF contient uniquement des images\n\n"
                                  "Utilisez 'Ouvrir avec l'application par défaut' pour essayer de l'ouvrir.")
        
        return text_edit
    
    def create_no_preview(self):
        """Créer un widget quand aucune prévisualisation n'est disponible"""
        widget = QWidget()
        widget.setStyleSheet("background-color: #ecf0f1;")
        layout = QVBoxLayout()
        
        # Icône et message
        icon_label = QLabel("📎")
        icon_label.setStyleSheet("font-size: 64px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        message = QLabel("Aucune prévisualisation disponible pour ce type de fichier")
        message.setAlignment(Qt.AlignCenter)
        message.setStyleSheet("color: #7f8c8d; font-size: 16px; padding: 20px;")
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Informations sur le type de fichier
        ext = Path(self.file.file_path).suffix[1:].upper()
        type_label = QLabel(f"Type de fichier: {ext}")
        type_label.setAlignment(Qt.AlignCenter)
        type_label.setStyleSheet("color: #95a5a6; font-size: 14px;")
        layout.addWidget(type_label)
        
        # Suggestion
        suggestion = QLabel("Cliquez sur 'Ouvrir avec l'application par défaut' pour visualiser ce fichier")
        suggestion.setAlignment(Qt.AlignCenter)
        suggestion.setStyleSheet("color: #3498db; font-size: 12px; margin-top: 20px;")
        suggestion.setWordWrap(True)
        layout.addWidget(suggestion)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def open_with_default(self):
        """Ouvrir le fichier avec l'application par défaut du système"""
        try:
            file_path = self.file.file_path
            
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "Erreur", "Le fichier n'existe plus à cet emplacement.")
                return
            
            # Ouvrir selon le système d'exploitation
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux et autres Unix
                subprocess.run(['xdg-open', file_path])
            
            self.statusBar().showMessage(f"Fichier ouvert: {self.file.name}", 3000)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Erreur", 
                f"Impossible d'ouvrir le fichier:\n{str(e)}\n\n"
                f"Assurez-vous qu'une application par défaut est configurée pour ce type de fichier."
            )
    
    def download_file(self):
        """Télécharger/exporter le fichier"""
        try:
            # Demander où enregistrer le fichier
            dest, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer le fichier",
                self.file.name,
                "Tous les fichiers (*.*)"
            )
            
            if dest:
                # Importer le contrôleur dynamiquement pour éviter les imports circulaires
                from controllers.file_controller import FileController
                
                file_controller = FileController(self.parent_window.user)
                success, message = file_controller.download_file(self.file.id, dest)
                
                if success:
                    QMessageBox.information(
                        self, 
                        "Succès", 
                        f"Fichier enregistré avec succès:\n{dest}"
                    )
                else:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement:\n{message}")
        
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Erreur", 
                f"Impossible de télécharger le fichier:\n{str(e)}"
            )
    
    def _format_timestamp(self, timestamp):
        """Formater un timestamp en date lisible"""
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%d/%m/%Y à %H:%M')




