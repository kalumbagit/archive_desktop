# models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean,Enum as SQLEnum
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.db_manager import Base
from utils.enums import UserRole, FolderVisibility



class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Rôle de l'utilisateur
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))
    
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    folders = relationship('Folder', back_populates='owner', cascade='all, delete-orphan')
    audit_logs = relationship('AuditLog', back_populates='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"
    
    def is_superuser(self):
        """Vérifie si l'utilisateur est un superuser"""
        return self.role == UserRole.SUPERUSER
    
    def is_admin(self):
        """Vérifie si l'utilisateur est admin ou superuser"""
        return self.role in [UserRole.ADMIN, UserRole.SUPERUSER]
    
    def can_access_folder(self, folder):
        """Vérifie si l'utilisateur peut accéder à un dossier"""
        # Superuser a accès à tout
        if self.is_superuser():
            return True
        
        # Propriétaire du dossier
        if folder.owner_id == self.id:
            return True
        
        # Dossier public
        if folder.visibility == FolderVisibility.PUBLIC:
            return True
        
        # Dossier partagé avec cet utilisateur
        if hasattr(folder, 'shared_with'):
            return any(share.user_id == self.id for share in folder.shared_with)
        
        return False