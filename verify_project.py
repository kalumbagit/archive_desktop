# verify_project.py
"""
Script de vérification complète du projet
Vérifie tous les fichiers, imports et dépendances
"""

import os
import sys
from pathlib import Path
import importlib.util

class ProjectVerifier:
    """Vérificateur de projet"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
        
    def check_file_exists(self, filepath):
        """Vérifier qu'un fichier existe"""
        path = Path(filepath)
        if path.exists():
            self.success.append(f"✓ {filepath}")
            return True
        else:
            self.errors.append(f"✗ MANQUANT: {filepath}")
            return False
    
    def check_directory_structure(self):
        """Vérifier la structure des dossiers"""
        print("=" * 60)
        print("1. VÉRIFICATION DE LA STRUCTURE")
        print("=" * 60)
        
        required_dirs = [
            'config',
            'database',
            'models',
            'controllers',
            'views',
            'utils',
            'resources/styles',
            'tests'
        ]
        
        for dir_path in required_dirs:
            if Path(dir_path).exists():
                self.success.append(f"✓ Dossier: {dir_path}/")
            else:
                self.errors.append(f"✗ Dossier manquant: {dir_path}/")
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                self.warnings.append(f"⚠ Créé: {dir_path}/")
        
        self.print_results()
    
    def check_python_files(self):
        """Vérifier les fichiers Python requis"""
        print("\n" + "=" * 60)
        print("2. VÉRIFICATION DES FICHIERS PYTHON")
        print("=" * 60)
        
        required_files = {
            # Root
            'main.py': 'Point d\'entrée principal',
            'setup_database.py': 'Configuration DB',
            'run_tests.py': 'Tests unitaires',
            'requirements.txt': 'Dépendances',
            
            # Config
            'config/__init__.py': 'Package config',
            'config/settings.py': 'Configuration',
            'config/database.py': 'Config DB',
            
            # Database
            'database/__init__.py': 'Package database',
            'database/db_manager.py': 'Gestionnaire DB',
            'database/migrations.py': 'Migrations',
            
            # Models
            'models/__init__.py': 'Package models',
            'models/user.py': 'Modèle User',
            'models/folder.py': 'Modèle Folder',
            'models/file.py': 'Modèle File',
            'models/audit_log.py': 'Modèle AuditLog',
            
            # Controllers
            'controllers/__init__.py': 'Package controllers',
            'controllers/auth_controller.py': 'Authentification',
            'controllers/folder_controller.py': 'Gestion dossiers',
            'controllers/file_controller.py': 'Gestion fichiers',
            'controllers/search_controller.py': 'Recherche',
            'controllers/audit_controller.py': 'Audit',
            
            # Views
            'views/__init__.py': 'Package views',
            'views/login_window.py': 'Fenêtre login',
            'views/register_window.py': 'Fenêtre inscription',
            'views/main_window.py': 'Fenêtre principale',
            'views/search_window.py': 'Fenêtre recherche',
            'views/import_window.py': 'Fenêtre import',
            'views/settings_window.py': 'Fenêtre paramètres',
            'views/preview_window.py': 'Fenêtre prévisualisation',
            'views/folder_dialog.py': 'Dialogue dossier',
            'views/folder_selection_dialog.py': 'Sélection dossier',
            
            # Utils
            'utils/__init__.py': 'Package utils',
            'utils/file_handler.py': 'Gestion fichiers',
            'utils/scanner.py': 'Scanner',
            'utils/preview_generator.py': 'Prévisualisation',
            'utils/validators.py': 'Validateurs',
            'utils/theme_manager.py': 'Thèmes',
            
            # Tests
            'tests/__init__.py': 'Package tests',
            'tests/test_models.py': 'Tests models',
            'tests/test_controllers.py': 'Tests controllers',
            'tests/test_utils.py': 'Tests utils',
        }
        
        for filepath, description in required_files.items():
            if self.check_file_exists(filepath):
                print(f"  ✓ {filepath:<45} [{description}]")
            else:
                print(f"  ✗ {filepath:<45} [MANQUANT - {description}]")
        
        self.print_results()
    
    def check_imports(self):
        """Vérifier les imports dans les fichiers clés"""
        print("\n" + "=" * 60)
        print("3. VÉRIFICATION DES IMPORTS")
        print("=" * 60)
        
        # Ajouter le répertoire courant au path
        sys.path.insert(0, os.getcwd())
        
        critical_imports = [
            ('config', 'Settings'),
            ('database.db_manager', 'DatabaseManager'),
            ('models.user', 'User'),
            ('controllers.auth_controller', 'AuthController'),
            ('views.login_window', 'LoginWindow'),
        ]
        
        for module_name, class_name in critical_imports:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    self.success.append(f"✓ Import OK: {module_name}.{class_name}")
                    print(f"  ✓ {module_name}.{class_name}")
                else:
                    self.errors.append(f"✗ Classe manquante: {module_name}.{class_name}")
                    print(f"  ✗ {module_name}.{class_name} - Classe introuvable")
            except ImportError as e:
                self.errors.append(f"✗ Import échoué: {module_name} - {str(e)}")
                print(f"  ✗ {module_name} - {str(e)}")
            except Exception as e:
                self.errors.append(f"✗ Erreur: {module_name} - {str(e)}")
                print(f"  ✗ {module_name} - {str(e)}")
        
        self.print_results()
    
    def check_dependencies(self):
        """Vérifier les dépendances Python"""
        print("\n" + "=" * 60)
        print("4. VÉRIFICATION DES DÉPENDANCES")
        print("=" * 60)
        
        required_packages = [
            'PySide6',
            'sqlalchemy',
            'werkzeug',
            'cryptography',
            'PIL',  # Pillow
            'PyPDF2',
        ]
        
        for package in required_packages:
            try:
                if package == 'PIL':
                    __import__('PIL')
                else:
                    __import__(package.lower())
                self.success.append(f"✓ {package} installé")
                print(f"  ✓ {package}")
            except ImportError:
                self.errors.append(f"✗ {package} NON installé")
                print(f"  ✗ {package} - Exécutez: pip install {package}")
        
        self.print_results()
    
    def check_content_key_files(self):
        """Vérifier le contenu des fichiers clés"""
        print("\n" + "=" * 60)
        print("5. VÉRIFICATION DU CONTENU DES FICHIERS CLÉS")
        print("=" * 60)
        
        key_patterns = {
            'main.py': ['QApplication', 'LoginWindow', 'MainWindow'],
            'views/main_window.py': ['class MainWindow', 'QMainWindow', 'def __init__'],
            'models/user.py': ['class User', 'Base', 'password'],
            'controllers/auth_controller.py': ['class AuthController', 'def login', 'def register'],
        }
        
        for filepath, patterns in key_patterns.items():
            if Path(filepath).exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                missing = [p for p in patterns if p not in content]
                
                if not missing:
                    self.success.append(f"✓ Contenu OK: {filepath}")
                    print(f"  ✓ {filepath} - Tous les éléments présents")
                else:
                    self.warnings.append(f"⚠ {filepath} - Éléments manquants: {missing}")
                    print(f"  ⚠ {filepath} - Manquants: {', '.join(missing)}")
            else:
                print(f"  ✗ {filepath} - Fichier inexistant")
        
        self.print_results()
    
    def print_results(self):
        """Afficher un résumé des résultats de la section"""
        if self.errors:
            print(f"\n  ❌ Erreurs: {len(self.errors)}")
        if self.warnings:
            print(f"  ⚠️  Avertissements: {len(self.warnings)}")
        if self.success:
            print(f"  ✅ Succès: {len(self.success)}")
    
    def generate_report(self):
        """Générer un rapport final"""
        print("\n" + "=" * 60)
        print("RAPPORT FINAL")
        print("=" * 60)
        
        total = len(self.success) + len(self.warnings) + len(self.errors)
        
        print(f"\n📊 Statistiques:")
        print(f"  Total de vérifications: {total}")
        print(f"  ✅ Succès: {len(self.success)}")
        print(f"  ⚠️  Avertissements: {len(self.warnings)}")
        print(f"  ❌ Erreurs: {len(self.errors)}")
        
        if self.errors:
            print(f"\n❌ ERREURS CRITIQUES ({len(self.errors)}):")
            for error in self.errors[:10]:  # Afficher les 10 premières
                print(f"  • {error}")
            if len(self.errors) > 10:
                print(f"  ... et {len(self.errors) - 10} autres erreurs")
        
        if self.warnings:
            print(f"\n⚠️  AVERTISSEMENTS ({len(self.warnings)}):")
            for warning in self.warnings[:5]:
                print(f"  • {warning}")
        
        print("\n" + "=" * 60)
        
        if not self.errors:
            print("✅ PROJET VALIDE - Prêt à être lancé!")
            print("\nCommandes suivantes:")
            print("  1. python setup_database.py")
            print("  2. python main.py")
        else:
            print("❌ PROJET INCOMPLET - Corrections nécessaires")
            print("\nActions recommandées:")
            print("  1. Vérifier que tous les fichiers sont créés")
            print("  2. Copier le contenu des artefacts correspondants")
            print("  3. Installer les dépendances: pip install -r requirements.txt")
            print("  4. Réexécuter ce script: python verify_project.py")
        
        print("=" * 60)
        
        return len(self.errors) == 0
    
    def run(self):
        """Exécuter toutes les vérifications"""
        print("\n🔍 VÉRIFICATION COMPLÈTE DU PROJET")
        print("Gestionnaire d'Archives Numériques\n")
        
        self.check_directory_structure()
        self.check_python_files()
        self.check_dependencies()
        self.check_imports()
        self.check_content_key_files()
        
        return self.generate_report()


def main():
    """Point d'entrée principal"""
    verifier = ProjectVerifier()
    success = verifier.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()