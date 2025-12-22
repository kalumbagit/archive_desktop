# models/folder.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.db_manager import Base
from utils.enums import  FolderVisibility

class Folder(Base):
    __tablename__ = 'folders'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    year = Column(Integer, nullable=True)
    theme = Column(String(100), nullable=True)
    sector = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Visibilité du dossier
    visibility = Column(SQLEnum(FolderVisibility), 
                       default=FolderVisibility.PRIVATE, 
                       nullable=False)
    
    # Relations
    parent_id = Column(Integer, ForeignKey('folders.id', ondelete='CASCADE'), nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    owner = relationship("User", back_populates="folders")
    
    # Relation parent (Many-to-One)
    parent = relationship(
        "Folder",
        remote_side=[id],
        back_populates="subfolders"
    )
    
    # Relation enfants (One-to-Many) avec cascade
    subfolders = relationship(
        "Folder",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_id]
    )
    
    # Cascade pour les fichiers
    files = relationship(
        "File",
        back_populates="folder",
        cascade="all, delete-orphan"
    )
    
    # Partages du dossier
    shared_with = relationship(
        "FolderShare",
        back_populates="folder",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Folder(id={self.id}, name='{self.name}', visibility='{self.visibility.value}')>"
    
    def is_public(self):
        """Vérifie si le dossier est public"""
        return self.visibility == FolderVisibility.PUBLIC
    
    def is_shared(self):
        """Vérifie si le dossier est partagé"""
        return self.visibility == FolderVisibility.SHARED