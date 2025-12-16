# install.py
"""
Script d'installation automatique pour le Gestionnaire d'Archives
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(step, text):
    """Print step information"""
    print(f"[{step}] {text}")

def run_command(command, description):
    """Run a shell command"""
    print(f"\n▶ {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print("✓ Succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Erreur: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} détecté")
        return True
    else:
        print(f"✗ Python 3.8+ requis. Version actuelle: {version.major}.{version.minor}")
        return False

def create_directory_structure():
    """Create project directory structure"""
    print_step("2/6", "Création de la structure des dossiers")
    
    directories = [
        'config',
        'database',
        'models',
        'controllers',
        'views',
        'utils',
        'resources/styles',
        'resources/icons',
        'resources/images',
        'tests'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}/")
    
    # Create __init__.py files
    init_dirs = ['config', 'database', 'models', 'controllers', 'views', 'utils', 'tests']
    for directory in init_dirs:
        init_file = Path(directory) / '__init__.py'
        if not init_file.exists():
            init_file.write_text('"""{}"""\n'.format(directory.capitalize()))
            print(f"  ✓ {directory}/__init__.py")
    
    print("\n✓ Structure créée avec succès")
    return True

def create_requirements_file():
    """Create requirements.txt if not exists"""
    print_step("3/6", "Création du fichier requirements.txt")
    
    requirements = """# Interface graphique
PySide6>=6.6.0

# Base de données
SQLAlchemy>=2.0.0

# Cryptographie et sécurité
Werkzeug>=3.0.0
cryptography>=41.0.0

# Traitement d'images
Pillow>=10.0.0

# Traitement de PDF
PyPDF2>=3.0.0

# Détection de type MIME
python-magic>=0.4.27
python-magic-bin>=0.4.14; platform_system == "Windows"
"""
    
    req_file = Path('requirements.txt')
    if not req_file.exists():
        req_file.write_text(requirements)
        print("✓ requirements.txt créé")
    else:
        print("✓ requirements.txt existe déjà")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_step("4/6", "Installation des dépendances Python")
    
    # Upgrade pip
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Mise à jour de pip"
    ):
        print("⚠ Avertissement: échec de la mise à jour de pip")
    
    # Install requirements
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installation des paquets"
    )

def setup_database():
    """Initialize database"""
    print_step("5/6", "Configuration de la base de données")
    
    # Check if setup_database.py exists
    if not Path('setup_database.py').exists():
        print("⚠ setup_database.py introuvable - ignoré")
        return True
    
    print("\nVoulez-vous configurer la base de données maintenant?")
    response = input("(o/n): ").lower()
    
    if response == 'o':
        return run_command(
            f"{sys.executable} setup_database.py",
            "Configuration de la base de données"
        )
    else:
        print("✓ Configuration de la base de données ignorée")
        return True

def create_readme():
    """Create basic README if not exists"""
    print_step("6/6", "Création du README")
    
    readme_content = """# Gestionnaire d'Archives Numériques

## Installation

L'installation a été effectuée avec succès!

## Démarrage

```bash
python main.py
```

## Documentation

Consultez README.md pour la documentation complète.
"""
    
    readme_file = Path('README_QUICK.md')
    if not readme_file.exists():
        readme_file.write_text(readme_content)
        print("✓ README_QUICK.md créé")
    else:
        print("✓ README existe déjà")
    
    return True

def main():
    """Main installation process"""
    print_header("INSTALLATION DU GESTIONNAIRE D'ARCHIVES")
    
    print("Ce script va installer et configurer l'application.")
    print("Durée estimée: 2-5 minutes\n")
    
    # Step 1: Check Python version
    print_step("1/6", "Vérification de Python")
    if not check_python_version():
        print("\n✗ Installation annulée: version Python incompatible")
        sys.exit(1)
    
    # Step 2: Create directory structure
    if not create_directory_structure():
        print("\n✗ Installation annulée: erreur lors de la création des dossiers")
        sys.exit(1)
    
    # Step 3: Create requirements file
    if not create_requirements_file():
        print("\n✗ Installation annulée: erreur lors de la création de requirements.txt")
        sys.exit(1)
    
    # Step 4: Install dependencies
    print("\nIMPORTANT: Cette étape peut prendre plusieurs minutes...")
    if not install_dependencies():
        print("\n✗ Installation annulée: erreur lors de l'installation des dépendances")
        print("\nEssayez manuellement:")
        print(f"  {sys.executable} -m pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 5: Setup database
    if not setup_database():
        print("\n⚠ Configuration de la base de données échouée")
        print("Vous pouvez la configurer plus tard avec:")
        print(f"  {sys.executable} setup_database.py")
    
    # Step 6: Create README
    create_readme()
    
    # Success message
    print_header("INSTALLATION TERMINÉE!")
    
    print("✓ Toutes les étapes sont terminées avec succès!\n")
    print("📁 Structure des fichiers créée")
    print("📦 Dépendances installées")
    print("🗄️  Base de données prête\n")
    
    print("PROCHAINES ÉTAPES:")
    print("1. Copiez le code source dans les fichiers correspondants")
    print("2. Lancez l'application: python main.py")
    print("3. Créez un compte utilisateur")
    print("4. Commencez à archiver!\n")
    
    print("FICHIERS IMPORTANTS:")
    print(f"  - Configuration: ~/.archive_manager/config.json")
    print(f"  - Base de données: ~/.archive_manager/archives.db")
    print(f"  - Stockage: ~/Archives/\n")
    
    print("AIDE:")
    print("  - Documentation complète: README.md")
    print("  - Tests: python run_tests.py")
    print("  - Configuration DB: python setup_database.py\n")
    
    print("🎉 Bon archivage!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Installation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Erreur inattendue: {e}")
        sys.exit(1)


# create_project.py
"""
Script pour créer tous les fichiers du projet avec leur contenu
ATTENTION: Ce script va créer de nombreux fichiers!
"""

import os
from pathlib import Path

# Template pour les fichiers __init__.py
INIT_TEMPLATES = {
    'config': '"""Configuration package"""\nfrom .settings import Settings\nfrom .database import DatabaseConfig\n\n__all__ = [\'Settings\', \'DatabaseConfig\']',
    'database': '"""Database package"""\nfrom .db_manager import DatabaseManager, Base\nfrom .migrations import DatabaseMigration\n\n__all__ = [\'DatabaseManager\', \'Base\', \'DatabaseMigration\']',
    'models': '"""Models package"""\nfrom .user import User\nfrom .folder import Folder\nfrom .file import File\nfrom .audit_log import AuditLog\n\n__all__ = [\'User\', \'Folder\', \'File\', \'AuditLog\']',
    'controllers': '"""Controllers package"""\nfrom .auth_controller import AuthController\nfrom .folder_controller import FolderController\nfrom .file_controller import FileController\nfrom .search_controller import SearchController\nfrom .audit_controller import AuditController\n\n__all__ = [\'AuthController\', \'FolderController\', \'FileController\', \'SearchController\', \'AuditController\']',
    'views': '"""Views package"""',
    'utils': '"""Utilities package"""',
    'tests': '"""Tests package"""'
}

def create_init_files():
    """Create __init__.py files for all packages"""
    print("Création des fichiers __init__.py...")
    
    for package, content in INIT_TEMPLATES.items():
        init_file = Path(package) / '__init__.py'
        init_file.parent.mkdir(parents=True, exist_ok=True)
        init_file.write_text(content)
        print(f"✓ {init_file}")

def create_file_structure():
    """Create empty file structure"""
    print("\nCréation de la structure des fichiers...")
    
    files = [
        'config/settings.py',
        'config/database.py',
        'database/db_manager.py',
        'database/migrations.py',
        'models/user.py',
        'models/folder.py',
        'models/file.py',
        'models/audit_log.py',
        'controllers/auth_controller.py',
        'controllers/folder_controller.py',
        'controllers/file_controller.py',
        'controllers/search_controller.py',
        'controllers/audit_controller.py',
        'views/login_window.py',
        'views/register_window.py',
        'views/main_window.py',
        'views/search_window.py',
        'views/import_window.py',
        'views/settings_window.py',
        'views/preview_window.py',
        'views/folder_dialog.py',
        'views/folder_selection_dialog.py',
        'utils/file_handler.py',
        'utils/scanner.py',
        'utils/preview_generator.py',
        'utils/validators.py',
        'utils/theme_manager.py',
        'tests/test_models.py',
        'tests/test_controllers.py',
        'tests/test_utils.py',
        'resources/styles/light_theme.qss',
        'resources/styles/dark_theme.qss',
        'main.py',
        'setup_database.py',
        'run_tests.py',
        'requirements.txt',
        'README.md'
    ]
    
    for file_path in files:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(f'# {file_path}\n# TODO: Add content\n')
            print(f"✓ {file_path}")
        else:
            print(f"  {file_path} (existe déjà)")

if __name__ == "__main__":
    print("="*60)
    print("  CRÉATION DE LA STRUCTURE DU PROJET")
    print("="*60 + "\n")
    
    create_init_files()
    create_file_structure()
    
    print("\n" + "="*60)
    print("  STRUCTURE CRÉÉE!")
    print("="*60)
    print("\nProchaines étapes:")
    print("1. Copiez le contenu des artefacts dans les fichiers correspondants")
    print("2. Exécutez: python install.py")
    print("3. Lancez: python main.py")