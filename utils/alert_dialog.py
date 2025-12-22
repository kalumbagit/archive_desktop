# utils/alert_dialog.py
from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtCore import Qt

class AlertDialog:
    """
    Classe utilitaire pour afficher des boîtes de dialogue uniformisées.
    Toutes les méthodes sont statiques et permettent d'afficher différents
    types d'alertes (information, warning, error, success, question, about).
    
    Caractéristiques :
    - Toujours centrées sur le parent qui les appelle.
    - Taille large pour un rendu professionnel.
    - Style et contenu uniformisés.
    """

    @staticmethod
    def _configure_box(parent: QWidget, title: str, message: str, icon: QMessageBox.Icon) -> QMessageBox:
        """
        Méthode interne pour configurer une boîte de dialogue standardisée.
        
        :param parent: Fenêtre parente (QWidget)
        :param title: Titre de la boîte
        :param message: Message à afficher
        :param icon: Icône de la boîte (QMessageBox.Icon)
        :return: QMessageBox configuré
        """
        box = QMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(message)
        box.setIcon(icon)
        box.setStandardButtons(QMessageBox.Ok)
        box.setDefaultButton(QMessageBox.Ok)

        # Toujours centré sur le parent
        box.setWindowModality(Qt.ApplicationModal)
        box.setWindowFlag(Qt.Dialog)
        box.setWindowFlag(Qt.WindowStaysOnTopHint)

        return box

    # ------------------------------
    # Méthodes publiques
    # ------------------------------

    @staticmethod
    def information(parent: QWidget, title: str, message: str):
        """Afficher une boîte d'information"""
        box = AlertDialog._configure_box(parent, title, message, QMessageBox.Information)
        box.exec()

    @staticmethod
    def warning(parent: QWidget, title: str, message: str):
        """Afficher une boîte d'avertissement"""
        box = AlertDialog._configure_box(parent, title, message, QMessageBox.Warning)
        box.exec()

    @staticmethod
    def error(parent: QWidget, title: str, message: str):
        """Afficher une boîte d'erreur"""
        box = AlertDialog._configure_box(parent, title, message, QMessageBox.Critical)
        box.exec()

    @staticmethod
    def success(parent: QWidget, title: str, message: str):
        """Afficher une boîte de succès (utilise l'icône Information par défaut)"""
        box = AlertDialog._configure_box(parent, title, message, QMessageBox.Information)
        box.setWindowTitle(f"✅ {title}")  # Ajouter un indicateur visuel
        box.exec()

    @staticmethod
    def question(parent: QWidget, title: str, message: str,
                 default: QMessageBox.StandardButton = QMessageBox.StandardButton.No) -> bool:
        """
        Afficher une boîte de question avec Oui/Non.
        
        :param parent: Fenêtre parente
        :param title: Titre de la boîte
        :param message: Message à afficher
        :param default: Bouton sélectionné par défaut (Yes ou No)
        :return: True si l'utilisateur choisit Oui, False sinon
        """
        box = QMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(message)
        box.setIcon(QMessageBox.Question)
        yes_btn = QMessageBox.StandardButton.Yes
        no_btn = QMessageBox.StandardButton.No
        box.setStandardButtons(yes_btn | no_btn)

        # Définir le bouton par défaut
        box.setDefaultButton(default)

        box.setWindowModality(Qt.ApplicationModal)
        box.setWindowFlag(Qt.Dialog)
        box.setWindowFlag(Qt.WindowStaysOnTopHint)

        result = box.exec()
        return result == yes_btn

    @staticmethod
    def about(parent: QWidget):
        """
        Afficher une boîte 'À propos' de l'application.
        
        :param parent: Fenêtre parente
        """
        message = (
            "Gestionnaire d'Archives Numériques\n\n"
            "Version 1.0.0\n"
            "Développé par Steve\n\n"
            "Cette application permet de gérer, partager et sécuriser vos archives numériques "
            "avec une interface moderne et professionnelle."
        )
        box = AlertDialog._configure_box(parent, "À propos", message, QMessageBox.Information)
        box.exec()
