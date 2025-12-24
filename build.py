#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py - Script de build automatique pour tous les OS
Usage: python build.py [--onefile] [--windowed] [--clean]
"""

import sys
import os
import platform
import subprocess
import shutil
import argparse
from pathlib import Path

class BuildManager:
    """Gestionnaire de build multi-plateforme"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / 'dist'
        self.build_dir = self.project_root / 'build'
        
    def clean(self):
        """Nettoyer les dossiers de build"""
        print("🧹 Nettoyage des dossiers de build...")
        
        dirs_to_clean = [self.dist_dir, self.build_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   ✓ Supprimé: {dir_path}")
        
        # Supprimer les fichiers .spec générés
        for spec_file in self.project_root.glob('*.spec'):
            if spec_file.name != 'archive_manager.spec':
                spec_file.unlink()
                print(f"   ✓ Supprimé: {spec_file}")
        
        print("✅ Nettoyage terminé\n")
    
    def check_dependencies(self):
        """Vérifier les dépendances"""
        print("🔍 Vérification des dépendances...")
        
        try:
            import PyInstaller
            print(f"   ✓ PyInstaller {PyInstaller.__version__}")
        except ImportError:
            print("   ❌ PyInstaller non installé")
            print("   Installation: pip install pyinstaller")
            return False
        
        try:
            import PySide6
            print(f"   ✓ PySide6")
        except ImportError:
            print("   ❌ PySide6 non installé")
            return False
        
        print("✅ Toutes les dépendances sont installées\n")
        return True
    
    def get_icon_path(self):
        """Obtenir le chemin de l'icône selon la plateforme"""
        assets_dir = self.project_root / 'assets'
        
        if self.platform == 'windows':
            icon_file = assets_dir / 'icon.ico'
        elif self.platform == 'darwin':
            icon_file = assets_dir / 'icon.icns'
        else:  # Linux
            icon_file = assets_dir / 'icon.png'
        
        if icon_file.exists():
            return str(icon_file)
        return None
    
    def build_with_spec(self):
        """Build avec le fichier .spec"""
        print(f"🔨 Build avec archive_manager.spec sur {self.platform}...")
        
        spec_file = self.project_root / 'archive_manager.spec'
        
        if not spec_file.exists():
            print(f"❌ Fichier {spec_file} introuvable")
            return False
        
        cmd = ['pyinstaller', '--clean', '--noconfirm', str(spec_file)]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
            print("✅ Build terminé avec succès\n")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors du build:")
            print(e.stderr)
            return False
    
    def build_simple(self, onefile=True, windowed=True):
        """Build simple sans fichier .spec"""
        print(f"🔨 Build simple sur {self.platform}...")
        
        cmd = [
            'pyinstaller',
            '--name=ArchiveManager',
            '--clean',
            '--noconfirm',
        ]
        
        if onefile:
            cmd.append('--onefile')
        else:
            cmd.append('--onedir')
        
        if windowed:
            cmd.append('--windowed')
        else:
            cmd.append('--console')
        
        # Ajouter l'icône
        icon_path = self.get_icon_path()
        if icon_path:
            cmd.append(f'--icon={icon_path}')
        
        # Hidden imports
        hidden_imports = [
            'PySide6.QtCore',
            'PySide6.QtGui',
            'PySide6.QtWidgets',
            'sqlalchemy.dialects.sqlite',
            'sqlalchemy.dialects.postgresql',
            'sqlalchemy.dialects.mysql',
            'magic',
            'bcrypt',
        ]
        
        for imp in hidden_imports:
            cmd.append(f'--hidden-import={imp}')
        
        # Fichier principal
        cmd.append('main.py')
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
            print("✅ Build terminé avec succès\n")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors du build:")
            print(e.stderr)
            return False
    
    def show_results(self):
        """Afficher les résultats du build"""
        print("📦 Résultats du build:")
        print(f"   Plateforme: {platform.system()} {platform.machine()}")
        
        if self.dist_dir.exists():
            print(f"\n   📁 Dossier de sortie: {self.dist_dir}")
            
            # Lister les fichiers
            files = list(self.dist_dir.rglob('*'))
            executables = [f for f in files if f.is_file() and 
                          (f.suffix in ['.exe', '.app', ''] and os.access(f, os.X_OK))]
            
            if executables:
                print("\n   ✅ Exécutables générés:")
                for exe in executables:
                    size = exe.stat().st_size / (1024 * 1024)  # MB
                    print(f"      • {exe.name} ({size:.1f} MB)")
            else:
                print("\n   📂 Contenu:")
                for item in self.dist_dir.iterdir():
                    print(f"      • {item.name}")
        else:
            print("   ❌ Aucun fichier généré")
    
    def create_installer_info(self):
        """Créer un fichier d'information pour l'installateur"""
        info_file = self.dist_dir / 'README.txt'
        
        content = f"""
Archive Manager - Gestionnaire d'Archives Numériques
Version 1.0.0

Plateforme: {platform.system()} {platform.machine()}
Date de build: {subprocess.check_output(['date']).decode().strip() if self.platform != 'windows' else 'N/A'}

INSTALLATION:
"""
        
        if self.platform == 'windows':
            content += """
Windows:
1. Double-cliquez sur ArchiveManager.exe
2. Ou copiez le fichier dans Program Files
3. Créez un raccourci sur le bureau si nécessaire

Configuration requise:
- Windows 10 ou supérieur
- 100 MB d'espace disque
"""
        elif self.platform == 'darwin':
            content += """
macOS:
1. Copiez ArchiveManager.app dans le dossier Applications
2. Au premier lancement, faites un clic droit > Ouvrir
   (pour autoriser l'application non signée)

Configuration requise:
- macOS 10.13 ou supérieur
- 150 MB d'espace disque
"""
        else:  # Linux
            content += """
Linux:
1. Rendez le fichier exécutable: chmod +x ArchiveManager
2. Lancez: ./ArchiveManager
3. Ou créez un lanceur dans votre menu

Configuration requise:
- Distribution Linux moderne (Ubuntu 20.04+, Fedora 33+, etc.)
- 100 MB d'espace disque
- Bibliothèques: libxcb, libGL
"""
        
        content += """

PREMIÈRE UTILISATION:
1. Créez un compte utilisateur
2. Configurez le dossier de stockage (Paramètres > Stockage)
3. Optionnel: Configurez le cloud (Paramètres > Cloud)

SUPPORT:
- Documentation: https://github.com/votre-repo
- Issues: https://github.com/votre-repo/issues

Copyright © 2024 - Tous droits réservés
"""
        
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n   📄 Fichier d'information créé: {info_file}")

def main():
    parser = argparse.ArgumentParser(description='Build Archive Manager')
    parser.add_argument('--clean', action='store_true', help='Nettoyer avant le build')
    parser.add_argument('--onefile', action='store_true', help='Build en un seul fichier')
    parser.add_argument('--windowed', action='store_true', default=True, help='Build sans console')
    parser.add_argument('--spec', action='store_true', help='Utiliser le fichier .spec')
    parser.add_argument('--simple', action='store_true', help='Build simple sans .spec')
    
    args = parser.parse_args()
    
    builder = BuildManager()
    
    print("=" * 60)
    print("🏗️  Archive Manager - Build Tool")
    print("=" * 60)
    print()
    
    # Nettoyage
    if args.clean:
        builder.clean()
    
    # Vérification
    if not builder.check_dependencies():
        sys.exit(1)
    
    # Build
    success = False
    if args.spec or (not args.simple and Path('archive_manager.spec').exists()):
        success = builder.build_with_spec()
    else:
        success = builder.build_simple(onefile=args.onefile, windowed=args.windowed)
    
    if success:
        builder.show_results()
        builder.create_installer_info()
        
        print("\n" + "=" * 60)
        print("✅ Build terminé avec succès!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Le build a échoué")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()