# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool, NullPool
from pathlib import Path

class DatabaseConfig:
    """Database configuration helper"""
    
    @staticmethod
    def get_sqlite_config(db_path=None):
        """Get SQLite database configuration"""
        if db_path is None:
            db_path = Path.home() / '.archive_manager' / 'archives.db'
        
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





