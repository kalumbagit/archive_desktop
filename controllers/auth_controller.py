# controllers/auth_controller.py
from database.db_manager import DatabaseManager
from models.user import User
from controllers.audit_controller import AuditController
from datetime import datetime

class AuthController:
    def __init__(self, db: DatabaseManager): 
        self.db = db
    
    def register(self, username, email, password):
        """Register a new user"""
        session = self.db.get_session()
        try:
            # Check if user exists
            existing = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing:
                return False, "Nom d'utilisateur ou email déjà utilisé"
            
            # Create new user
            user = User(username=username, email=email)
            user.set_password(password)
            
            session.add(user)
            session.commit()
            
            return True, "Inscription réussie"
        except Exception as e:
            session.rollback()
            return False, f"Erreur: {str(e)}"
        finally:
            session.close()
    
    def login(self, username, password):
        """Authenticate user"""
        session = self.db.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            
            if user and user.check_password(password) and user.is_active:
                user.last_login = datetime.utcnow()
                session.commit()
                
                # Log login action
                audit = AuditController(user)
                audit.log_action('LOGIN', 'USER', user.id, 'Connexion réussie')
                
                return True, user
            
            return False, "Identifiants incorrects"
        except Exception as e:
            return False, f"Erreur: {str(e)}"
        finally:
            session.close()


