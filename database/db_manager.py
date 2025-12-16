# database/db_manager.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os
from pathlib import Path

Base = declarative_base()

class DatabaseManager:
    _instance = None
    _engine = None
    _session_factory = None
    
    def _new_(cls):
        if cls._instance is None:
            cls.instance = super().new_(cls)
        return cls._instance
    
    def initialize(self, db_type='sqlite', db_path=None, **kwargs):
        """
        Initialize database connection
        
        Args:
            db_type: 'sqlite', 'postgresql', 'mysql'
            db_path: Path to SQLite database file
            **kwargs: Additional database connection parameters
        """
        if db_type == 'sqlite':
            if db_path is None:
                db_path = Path.home() / '.archive_manager' / 'archives.db'
            
            # Create directory if it doesn't exist
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            connection_string = f'sqlite:///{db_path}'
            self._engine = create_engine(
                connection_string,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool
            )
        
        elif db_type == 'postgresql':
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 5432)
            database = kwargs.get('database', 'archive_manager')
            user = kwargs.get('user', 'postgres')
            password = kwargs.get('password', '')
            
            connection_string = f'postgresql://{user}:{password}@{host}:{port}/{database}'
            self._engine = create_engine(connection_string)
        
        elif db_type == 'mysql':
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 3306)
            database = kwargs.get('database', 'archive_manager')
            user = kwargs.get('user', 'root')
            password = kwargs.get('password', '')
            
            connection_string = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
            self._engine = create_engine(connection_string)
        
        # Create session factory
        self._session_factory = sessionmaker(bind=self._engine)
        
        # Create all tables
        Base.metadata.create_all(self._engine)
    
    def get_session(self):
        """Get a new database session"""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._session_factory()
    
    def close(self):
        """Close database connection"""
        if self._engine:
            self._engine.dispose()


