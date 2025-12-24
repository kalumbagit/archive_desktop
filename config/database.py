from sqlalchemy.pool import StaticPool, NullPool
from pathlib import Path
from utils.path_config import load_resource
from config.settings import Settings

class DatabaseConfig:
    """Database configuration helper"""

    @staticmethod
    def get_sqlite_config(db_path=None):
        """Get SQLite database configuration"""
        settings = Settings()
        
        # Lire le chemin depuis la config si non fourni
        if db_path is None:
            db_path = settings.get("database.path")
        
        # Si packagé avec PyInstaller, essayer de charger via load_resource
        try:
            # ⚡ Charger le fichier SQLite packagé
            db_path = Path(load_resource("ressources/database/archives.db", mode="text"))
        except FileNotFoundError:
            # ⚡ Fallback : utiliser le chemin défini dans config.json
            db_path = Path(db_path)

        # Créer le dossier si nécessaire
        db_path.parent.mkdir(parents=True, exist_ok=True)

        return {
            'url': f'sqlite:///{db_path}',
            'connect_args': {'check_same_thread': False},
            'poolclass': StaticPool,
            'echo': False
        }

    @staticmethod
    def get_postgresql_config(host='localhost', port=5432, 
                             database='archive_manager', 
                             user='postgres', password=''):
        """Get PostgreSQL database configuration"""
        return {
            'url': f'postgresql://{user}:{password}@{host}:{port}/{database}',
            'poolclass': NullPool,
            'echo': False
        }

    @staticmethod
    def get_mysql_config(host='localhost', port=3306,
                        database='archive_manager',
                        user='root', password=''):
        """Get MySQL database configuration"""
        return {
            'url': f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}',
            'poolclass': NullPool,
            'echo': False
        }
