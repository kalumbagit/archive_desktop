# views/search_window.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QTableWidget,
                               QTableWidgetItem, QHeaderView, QSpinBox)
from PySide6.QtCore import Qt
from controllers.folder_controller import FolderController
from database.db_manager import DatabaseManager

class SearchWindow(QDialog):
    def __init__(self, parent, db: DatabaseManager):
        super().__init__(parent)
        self.user = parent.user
        self.db=db
        self.folder_controller = FolderController(self.user,self.db)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Recherche avancée")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout()
        
        # Search criteria
        criteria_layout = QVBoxLayout()
        
        # Name/keyword search
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Mot-clé:"))
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Rechercher dans les noms et descriptions")
        name_layout.addWidget(self.keyword_input)
        criteria_layout.addLayout(name_layout)
        
        # Year filter
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Année:"))
        self.year_input = QSpinBox()
        self.year_input.setRange(0, 2100)
        self.year_input.setSpecialValueText("Toutes")
        self.year_input.setValue(0)
        year_layout.addWidget(self.year_input)
        year_layout.addStretch()
        criteria_layout.addLayout(year_layout)
        
        # Theme filter
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Thème:"))
        self.theme_input = QLineEdit()
        self.theme_input.setPlaceholderText("Ex: Finances, RH, Juridique...")
        theme_layout.addWidget(self.theme_input)
        criteria_layout.addLayout(theme_layout)
        
        # Sector filter
        sector_layout = QHBoxLayout()
        sector_layout.addWidget(QLabel("Secteur:"))
        self.sector_input = QLineEdit()
        self.sector_input.setPlaceholderText("Ex: Commercial, Technique...")
        sector_layout.addWidget(self.sector_input)
        criteria_layout.addLayout(sector_layout)
        
        # Search type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Tous", "Dossiers", "Fichiers (cette fonctionnalité n'est pas encore implémentée)"])
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        criteria_layout.addLayout(type_layout)
        
        layout.addLayout(criteria_layout)
        
        # Search button
        search_btn = QPushButton("Rechercher")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        search_btn.clicked.connect(self.perform_search)
        layout.addWidget(search_btn)
        
        # Results table
        results_label = QLabel("Résultats de la recherche:")
        results_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(results_label)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Nom", "Type", "Année", "Thème", "Secteur"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.doubleClicked.connect(self.open_result)
        layout.addWidget(self.results_table)
        
        # Close button
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def perform_search(self):
        """Execute search with given criteria"""
        keyword = self.keyword_input.text().strip()
        year = self.year_input.value() if self.year_input.value() > 0 else None
        theme = self.theme_input.text().strip() or None
        sector = self.sector_input.text().strip() or None

        # Search folders
        folders = self.folder_controller.search_folders(
            query=keyword,
            year=year,
            theme=theme,
            sector=sector
        )
   

        # Display results
        self.results_table.setRowCount(0)
        
        for folder in folders:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            self.results_table.setItem(row, 0, QTableWidgetItem(folder.name))
            self.results_table.setItem(row, 1, QTableWidgetItem("Dossier"))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(folder.year or "")))
            self.results_table.setItem(row, 3, QTableWidgetItem(folder.theme or ""))
            self.results_table.setItem(row, 4, QTableWidgetItem(folder.sector or ""))
            
            # Store folder object
            self.results_table.item(row, 0).setData(Qt.UserRole, folder)
    
    """def open_result(self, index):
        \"""Open selected result\"""
        row = index.row()
        item = self.results_table.item(row, 0)
        result = item.data(Qt.UserRole)
        
        # TODO: Open folder or file preview
        print(f"Opening: {result.name}")
        """


    def open_result(self, index):
        """Open selected result in folder view"""
        row = index.row()
        item = self.results_table.item(row, 0)
        folder = item.data(Qt.UserRole)
        
        if folder:
            # Ouvrir la fenêtre de visualisation du dossier
            from views.folder_view_window import FolderViewWindow
            folder_view = FolderViewWindow(folder, self.user, self.db, self)
            folder_view.exec()

