# database/db_manager.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from pathlib import Path
from utils.path_config import load_resource

Base = declarative_base()

class DatabaseManager:
    _instance = None
    _engine = None
    _session_factory = None
    _db_type = None # <-- ajouté pour stocker le type de base de données
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, db_type='sqlite', db_path=None, **kwargs):
        self._db_type = db_type # <-- stocker le type
        """
        Initialize database connection
        
        Args:
            db_type: 'sqlite', 'postgresql', 'mysql'
            db_path: Path to SQLite database file (string or Path)
            **kwargs: Additional database connection parameters
        """
        if db_type == 'sqlite':
            if db_path is None:
                # ⚠️ Ici on utilise load_resource pour retrouver le chemin
                try:
                    db_path = load_resource("ressources/database/archives.db", mode="text")
                except FileNotFoundError:
                    # fallback si le fichier n’est pas packagé
                    db_path = Path.home() / '.archive_manager' / 'archives.db'
            else:
                # Toujours convertir en Path pour éviter l'erreur .parent
                db_path = Path(db_path)
            
            # Créer le dossier si nécessaire
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
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        # Créer la session factory
        self._session_factory = sessionmaker(bind=self._engine)
        
        # Créer toutes les tables définies dans Base
        Base.metadata.create_all(self._engine)
    
    def get_session(self):
        """Get a new database session"""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._session_factory()
    
    def get_db_type(self):
        """Retourne le type de base de données (sqlite, postgresql, mysql)""" 
        return self._db_type
    
    def close(self):
        """Close database connection"""
        if self._engine:
            self._engine.dispose()
