# -*- mode: python ; coding: utf-8 -*-
# =============================================================================
# archive_manager.spec - Configuration PyInstaller COMPLÈTE
# Compatible Windows, macOS, Linux
# =============================================================================

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collecter les données des packages
datas = []
datas += collect_data_files('PySide6')
datas += collect_data_files('sqlalchemy')

# Ajouter explicitement tes fichiers de style
datas += [
    ('ressources/styles/colors.qss', 'ressources/styles'),
    ('ressources/styles/dark_theme.qss', 'ressources/styles'),
    ('ressources/styles/light_theme.qss', 'ressources/styles'),
]


# ============================================================================
# MODULES CACHÉS - TOUS LES IMPORTS DE L'APPLICATION
# ============================================================================
hiddenimports = [
    # ========== PySide6 (Interface graphique) ==========
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',
    
    # ========== SQLAlchemy (Base de données) ==========
    'sqlalchemy',
    'sqlalchemy.orm',
    'sqlalchemy.ext.declarative',
    'sqlalchemy.pool',
    'sqlalchemy.dialects',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.dialects.postgresql',
    'sqlalchemy.dialects.mysql',
    'sqlalchemy.sql',
    'sqlalchemy.sql.sqltypes',
    'sqlalchemy.sql.schema',
    
    # Drivers de base de données
    'psycopg2',
    'pymysql',
    
    # ========== Modules Python standard ==========
    'pathlib',
    'json',
    'shutil',
    'datetime',
    'enum',
    're',
    'os',
    'sys',
    'hashlib',
    'hmac',
    'base64',
    'uuid',
    'tempfile',
    'threading',
    
    # ========== Sécurité ==========
    'bcrypt',
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.backends',
    
    # ========== Détection de fichiers ==========
    'magic',
    'mimetypes',
    
    # ========== Cloud Storage ==========
    'boto3',
    'boto3.session',
    'botocore',
    'botocore.client',
    'botocore.exceptions',
    'azure.storage.blob',
    'azure.core',
    'azure.core.exceptions',
    'google.cloud.storage',
    'google.auth',
    'google.auth.credentials',
    'ftplib',
    
    # ========== Modules de l'application ==========
    # Base de données
    'database',
    'database.db_manager',
    'database.migrations',
    
    # Modèles
    'models',
    'models.user',
    'models.folder',
    'models.file',
    'models.folder_share',
    'models.audit_log',
    
    # Contrôleurs
    'controllers',
    'controllers.auth_controller',
    'controllers.audit_controller',
    'controllers.cloud_storage',
    'controllers.file_controller',
    'controllers.folder_controller',
    'controllers.search_controller',
    'controllers.sharing_controller',
    
    # Vues
    'views',
    'views.file_creation_dialog',
    'views.folder_dialog',
    'views.folder_selection_dialog',
    'views.folder_view_window',
    'views.folder_view',
    'views.import_window',
    'views.login_window',
    'views.main_window',
    'views.manage_shares_dialog',
    'views.preview_window',
    'views.register_window',
    'views.search_window',
    'views.settings_window',
    'views.share_dialog',
    
    # Configuration
    'config',
    'config.settings',
    'config.database',
    
    
    # Utilitaires
    'utils',
    'utils.alert_dialog',
    'utils.enums',
    'utils.file_handler',
    'utils.preview_generator',
    'utils.scanner',
    'utils.theme_manager',
    'utils.validators',
    'utils.path_config',
]

# Collecter tous les sous-modules de packages importants
hiddenimports += collect_submodules('sqlalchemy')
hiddenimports += collect_submodules('PySide6')
hiddenimports += collect_submodules('bcrypt')
hiddenimports += collect_submodules('cryptography')

# ============================================================================
# ANALYSE
# ============================================================================
a = Analysis(
    ['main.py'],
    pathex=['.'],  # Ajouter le répertoire courant
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclure les packages non nécessaires pour réduire la taille
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'sphinx',
        'PIL',
        'setuptools',
        'distutils',
        'tkinter',
        'test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ============================================================================
# PYZ (Archive Python)
# ============================================================================
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# ============================================================================
# CONFIGURATION SELON LA PLATEFORME
# ============================================================================

if sys.platform == 'win32':
    # ========== WINDOWS ==========
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='ArchiveManager',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # False pour application GUI (pas de console)
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
        version='version_info.txt' if os.path.exists('version_info.txt') else None,
    )

elif sys.platform == 'darwin':
    # ========== macOS ==========
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='ArchiveManager',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='assets/icon.icns' if os.path.exists('assets/icon.icns') else None,
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='ArchiveManager',
    )
    
    app = BUNDLE(
        coll,
        name='ArchiveManager.app',
        icon='assets/icon.icns' if os.path.exists('assets/icon.icns') else None,
        bundle_identifier='com.archivemanager.app',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'CFBundleName': 'Archive Manager',
            'CFBundleDisplayName': 'Archive Manager',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHumanReadableCopyright': 'Copyright © 2024',
            'LSMinimumSystemVersion': '10.13.0',
            'NSRequiresAquaSystemAppearance': 'False',
        },
    )

else:
    # ========== LINUX ==========
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='ArchiveManager',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='assets/icon.png' if os.path.exists('assets/icon.png') else None,
    )