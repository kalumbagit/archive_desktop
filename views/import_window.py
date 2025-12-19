


# views/import_window.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QListWidget, QFileDialog, 
                               QProgressBar, QMessageBox, QCheckBox)
from PySide6.QtCore import Qt
from controllers.file_controller import FileController
from controllers.folder_controller import FolderController
import os
from database.db_manager import DatabaseManager

class ImportWindow(QDialog):
    def __init__(self, parent,db: DatabaseManager):
        super().__init__(parent)
        self.user = parent.user
        self.db=db
        self.file_controller = FileController(self.user,self.db)
        self.folder_controller = FolderController(self.user,self.db)
        self.selected_files = []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Importer des fichiers")
        self.setGeometry(200, 200, 700, 500)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Sélection et import de fichiers")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Options
        options_layout = QHBoxLayout()
        
        self.scan_folders_cb = QCheckBox("Scanner les sous-dossiers")
        self.scan_folders_cb.setChecked(True)
        options_layout.addWidget(self.scan_folders_cb)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Selection buttons
        buttons_layout = QHBoxLayout()
        
        select_files_btn = QPushButton("Sélectionner des fichiers")
        select_files_btn.clicked.connect(self.select_files)
        buttons_layout.addWidget(select_files_btn)
        
        select_folder_btn = QPushButton("Sélectionner un dossier")
        select_folder_btn.clicked.connect(self.select_folder)
        buttons_layout.addWidget(select_folder_btn)
        
        clear_btn = QPushButton("Effacer la liste")
        clear_btn.clicked.connect(self.clear_list)
        buttons_layout.addWidget(clear_btn)
        
        layout.addLayout(buttons_layout)
        
        # File list
        list_label = QLabel("Fichiers sélectionnés:")
        layout.addWidget(list_label)
        
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)
        
        # Destination folder selection
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Dossier de destination:"))
        
        self.dest_label = QLabel("Aucun dossier sélectionné")
        self.dest_label.setStyleSheet("color: #e74c3c;")
        dest_layout.addWidget(self.dest_label)
        
        select_dest_btn = QPushButton("Choisir")
        select_dest_btn.clicked.connect(self.select_destination)
        dest_layout.addWidget(select_dest_btn)
        
        dest_layout.addStretch()
        layout.addLayout(dest_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("Importer")
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.import_btn.clicked.connect(self.import_files)
        self.import_btn.setEnabled(False)
        action_layout.addWidget(self.import_btn)
        
        cancel_btn = QPushButton("Fermer")
        cancel_btn.clicked.connect(self.close)
        action_layout.addWidget(cancel_btn)
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
    
    def select_files(self):
        """Open file selection dialog"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner des fichiers",
            "",
            "Tous les fichiers (*.*)"
        )
        
        if files:
            for file_path in files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    self.file_list.addItem(os.path.basename(file_path))
            
            self.update_import_button()
    
    def select_folder(self):
        """Open folder selection dialog and scan for files"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner un dossier"
        )
        
        if folder:
            files = []
            
            if self.scan_folders_cb.isChecked():
                # Recursive scan
                for root, dirs, filenames in os.walk(folder):
                    for filename in filenames:
                        files.append(os.path.join(root, filename))
            else:
                # Only direct children
                files = [os.path.join(folder, f) for f in os.listdir(folder)
                        if os.path.isfile(os.path.join(folder, f))]
            
            for file_path in files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    self.file_list.addItem(os.path.basename(file_path))
            
            self.update_import_button()
    
    def clear_list(self):
        """Clear selected files"""
        self.selected_files.clear()
        self.file_list.clear()
        self.update_import_button()
    
    def select_destination(self):
        """Select destination folder from archive"""
        # TODO: Implement folder selection dialog from archive folders
        from views.folder_selection_dialog import FolderSelectionDialog
        dialog = FolderSelectionDialog(self, self.user)
        if dialog.exec():
            self.destination_folder = dialog.selected_folder
            self.dest_label.setText(self.destination_folder.name)
            self.dest_label.setStyleSheet("color: #27ae60;")
            self.update_import_button()
    
    def update_import_button(self):
        """Enable/disable import button"""
        has_files = len(self.selected_files) > 0
        has_destination = hasattr(self, 'destination_folder')
        self.import_btn.setEnabled(has_files and has_destination)
    
    def import_files(self):
        """Import selected files"""
        if not hasattr(self, 'destination_folder'):
            QMessageBox.warning(self, "Erreur", 
                              "Veuillez sélectionner un dossier de destination")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.selected_files))
        
        success_count = 0
        failed_count = 0
        
        for i, file_path in enumerate(self.selected_files):
            self.progress_bar.setValue(i + 1)
            
            success, result = self.file_controller.add_file(
                file_path,
                self.destination_folder.id
            )
            
            if success:
                success_count += 1
            else:
                failed_count += 1
        
        self.progress_bar.setVisible(False)
        
        # Show result
        message = f"Import terminé:\n{success_count} fichier(s) importé(s)"
        if failed_count > 0:
            message += f"\n{failed_count} échec(s)"
        
        QMessageBox.information(self, "Import terminé", message)
        
        self.clear_list()
