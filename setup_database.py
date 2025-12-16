# setup_database.py
"""Script to set up the database"""
from database.db_manager import DatabaseManager
from database.migrations import DatabaseMigration
from config.settings import Settings

def setup_database():
    """Initialize and set up database"""
    print("=== Configuration de la base de données ===\n")
    
    # Initialize database
    db = DatabaseManager()
    settings = Settings()
    
    db_config = settings.get('database')
    db.initialize(
        db_type=db_config.get('type', 'sqlite'),
        db_path=db_config.get('path')
    )
    
    print(f"✓ Base de données initialisée: {db_config.get('type', 'sqlite')}")
    
    # Run migrations
    migration = DatabaseMigration()
    
    print("\n=== Création des tables ===")
    migration.create_all_tables()
    
    # Create admin user
    print("\n=== Création de l'utilisateur admin ===")
    create_admin = input("Créer un utilisateur admin? (o/n): ").lower()
    
    if create_admin == 'o':
        username = input("Nom d'utilisateur (admin): ") or "admin"
        email = input("Email (admin@local): ") or "admin@local"
        password = input("Mot de passe (admin123): ") or "admin123"
        
        migration.create_initial_admin(username, email, password)
    
    print("\n✓ Configuration terminée!")

if __name__ == "__main__":
    setup_database()