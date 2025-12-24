# database/migrations.py
from sqlalchemy import inspect
from database.db_manager import DatabaseManager, Base


class DatabaseMigration:
    """Handle database migrations and schema updates"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_all_tables(self):
        """Create all tables if they don't exist"""
        try:
            Base.metadata.create_all(self.db._engine)
            print("✓ Tables créées avec succès")
            return True
        except Exception as e:
            print(f"✗ Erreur lors de la création des tables: {e}")
            return False
    
    def drop_all_tables(self):
        """Drop all tables (use with caution!)"""
        try:
            Base.metadata.drop_all(self.db._engine)
            print("✓ Tables supprimées avec succès")
            return True
        except Exception as e:
            print(f"✗ Erreur lors de la suppression des tables: {e}")
            return False
    
    def check_table_exists(self, table_name):
        """Check if a table exists"""
        inspector = inspect(self.db._engine)
        return table_name in inspector.get_table_names()
    
    def get_existing_tables(self):
        """Get list of existing tables"""
        inspector = inspect(self.db._engine)
        return inspector.get_table_names()
    
    def reset_database(self):
        """Reset database (drop and recreate all tables)"""
        print("⚠️  Réinitialisation de la base de données...")
        self.drop_all_tables()
        self.create_all_tables()
        print("✓ Base de données réinitialisée")
    
    def add_column(self, table_name, column_name, column_type):
        """Add a new column to an existing table"""
        # Note: SQLite has limited ALTER TABLE support
        # For production, use Alembic for migrations
        pass
    
    def create_initial_admin(self, username='admin', email='admin@local', password='admin123'):
        """Create initial admin user"""
        from controllers.auth_controller import AuthController
        
        auth = AuthController()
        success, message = auth.register(username, email, password)
        
        if success:
            print(f"✓ Utilisateur admin créé: {username}")
            return True
        else:
            print(f"✗ Erreur lors de la création de l'admin: {message}")
            return False
